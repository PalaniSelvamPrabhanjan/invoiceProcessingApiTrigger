import json
import pandas as pd
from datetime import datetime
import joblib

# -----------------------------------------------------------------------------
# 0) Helper: merge existing flagged reasons into each invoice dict
# -----------------------------------------------------------------------------
def merge_existing_flags(extracted_list, flagged_list):
    """
    For each invoice in extracted_list, add a 'FlaggedReason' key
    containing the list from flagged_list (matched by CurrentAttachment),
    or [] if none.
    """
    # build lookup from attachment -> reasons
    lookup = {
        f["CurrentAttachment"]: f.get("FlaggedReason", [])
        for f in flagged_list
    }
    for inv in extracted_list:
        inv["FlaggedReason"] = lookup.get(inv.get("SourceFileName"), []).copy()

# -----------------------------------------------------------------------------
# 1) Load model once at import time
# -----------------------------------------------------------------------------
_import_errors = []
try:
    model = joblib.load(
        r"C:\Users\Palan\Desktop\projectA\pythonFiles\xgb_fraud_model.joblib"
    )
except Exception as e:
    model = None
    _import_errors.append(f"Failed to load fraud model: {e}")

# -----------------------------------------------------------------------------
# 2) Feature builder: keep only the five features model expects
# -----------------------------------------------------------------------------
def make_features(inv: dict, po: dict) -> pd.DataFrame:
    row = dict(inv)
    for k, v in po.items():
        row[f"PO_{k}" if not k.startswith("PO_") else k] = v

    df = pd.DataFrame([row])
    df["ExpectedDate"] = pd.to_datetime(df["ExpectedDate"], errors="coerce")
    today = pd.to_datetime(datetime.today().date())
    df["IsDueSoon"] = ((df["ExpectedDate"] - today).dt.days < 2).astype(int)

    keep = {"InvoiceSubTotal", "InvoiceTax", "InvoiceTotal", "PO_Amount", "IsDueSoon"}
    drop_cols = [c for c in df.columns if c not in keep]
    return df.drop(columns=drop_cols)

# -----------------------------------------------------------------------------
# 3) Main entrypoint: returns ExtractedInvoiceJson, SuccessfulInvoiceJson, ExecutionError
# -----------------------------------------------------------------------------
def validate_invoices(extracted_json, purchase_order_json, flagged_json):
    executionError = ""

    # 3a) import-time errors?
    if _import_errors:
        executionError = "; ".join(_import_errors)
        # still merge flags so extracted_out has an empty or original FlaggedReason field
        try:
            extracted = json.loads(extracted_json)
        except:
            extracted = []
        merge_existing_flags(extracted, [])
        success_json = json.dumps([inv for inv in extracted if inv.get("ExtractionStatus") != "Failed"])
        return json.dumps(extracted), success_json, executionError

    # 3b) parse inputs
    try:
        extracted = json.loads(extracted_json)
        purchase  = json.loads(purchase_order_json)
        flagged   = json.loads(flagged_json)
    except Exception as e:
        executionError = f"JSON parsing error: {e}"
        try:
            extracted = json.loads(extracted_json)
        except:
            extracted = []
        merge_existing_flags(extracted, [])
        success_json = json.dumps([inv for inv in extracted if inv.get("ExtractionStatus") != "Failed"])
        return json.dumps(extracted), success_json, executionError

    # merge in any existing flagged reasons
    merge_existing_flags(extracted, flagged)

    # 3c) business logic
    for inv in extracted:
        reasons = inv["FlaggedReason"]  # start with existing

        # run checks
        try:
            po = next((p for p in purchase if p.get("PO_No") == inv.get("PO_No")), None)
            if not po:
                reasons.append("No purchase order for invoice")
            else:
                if model is None:
                    executionError = "Model unavailable for fraud check"
                    break
                pred = bool(model.predict(make_features(inv, po))[0])
                if pred:
                    reasons.append("Model predicts invoice as fraud")

                if inv.get("InvoiceTotal") != po.get("PO_Amount"):
                    reasons.append(
                        f"InvoiceTotal ({inv.get('InvoiceTotal')}) "
                        f"does not match PO_Amount ({po.get('PO_Amount')})"
                    )
                if inv.get("VendorName") != po.get("VendorName"):
                    reasons.append(
                        f"VendorName ({inv.get('VendorName')}) "
                        f"does not match PO VendorName ({po.get('VendorName')})"
                    )
                if inv.get("Invoice_LineItems") != po.get("PO_LineItems"):
                    reasons.append("Invoice_LineItems do not match PO_LineItems")

        except Exception as ex:
            reasons.append(f"Python processing error for invoice {inv.get('InvoiceNo')}: {ex}")

        # update status
        if reasons:
            inv["ExtractionStatus"] = "Failed"
        else:
            inv["ExtractionStatus"] = "Successful"

        if executionError:
            break

    # 3d) serialize outputs
    extracted_out = json.dumps(extracted)
    success_out   = json.dumps([inv for inv in extracted if inv.get("ExtractionStatus") != "Failed"])
    return extracted_out, success_out, executionError
