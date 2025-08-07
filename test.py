# local_test.py

import json
import datetime
from invoiceValidation import validate_invoices

def log_uipath(message, level="Information", logType="User", fileName="Main"):
    entry = {
        "message": message,
        "level":    level,
        "logType":  logType,
        "timeStamp": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "fileName": fileName,
        # you can add jobId, robotName, etc. if you like
    }
    print(json.dumps(entry))

if __name__ == "__main__":
    # 1) your extracted invoices JSON
    extracted_json = r'''[{"InvoiceNo":"INV-001","PO_No":"PO-001","Invoice_LineItems":[{"ItemName":"Packaging Mockups (3.5KUs)","UnitPrice":"120","Quantity":"3","Total":"1573"},{"ItemName":"Logo Redesign","UnitPrice":"650","Quantity":"1","Total":"650"},{"ItemName":"Brand Guidelines Document","UnitPrice":"450","Quantity":"1","Total":"450"}],"ExpectedDate":"2025-06-30T00:00:00","VendorName":"Alpha Supplies","InvoiceSubTotal":2673.0,"InvoiceTax":10.0,"InvoiceTotal":2940.30,"SourceFileName":"14.jpg","SourceFileType":"PDF Image","ExtractionTime":"2025-08-05T15:57:06.8828149","ExtractionStatus":"Failed"},{"InvoiceNo":"INV-674","PO_No":null,"Invoice_LineItems":[{"ItemName":"Whiteboard","UnitPrice":"150.00","Quantity":"4","Total":"600"}],"ExpectedDate":"2025-07-12T00:00:00","VendorName":"TATA Salts","InvoiceSubTotal":1100.0,"InvoiceTax":null,"InvoiceTotal":null,"SourceFileName":"Simple Minimalist Business Invoice (1).pdf","SourceFileType":"PDF","ExtractionTime":"2025-08-05T15:57:07.4664459","ExtractionStatus":"Failed"}]'''

    # 2) your purchase orders JSON
    purchase_order_json = r'''[{"PO_No":"PO-001","VendorName":"Alpha Supplies","PO_LineItems":[{"ItemName":"Staplers","ItemPrice":"10.00","ItemQuantity":"10","ItemPriceTotal":"100.00"},{"ItemName":"A4 Paper","ItemPrice":"20.00","ItemQuantity":"20","ItemPriceTotal":"400.00"},{"ItemName":"Folders","ItemPrice":"20.00","ItemQuantity":"25","ItemPriceTotal":"500.00"}],"PO_Amount":1200.00,"PaymentDueDate":"2025-07-01T00:00:00","PaymentStatus":"Completed","ExtractionStatus":"Extracted"}, … ]'''  # truncate for brevity—paste your full JSON here

    # 3) your initially flagged list JSON
    flagged_json = r'''[{"CurrentAttachment":"14.jpg","ExtractionTime":"2025-08-05T15:59:01.7846728","FlaggedReason":["Invoice is a duplicate of previously processed invoices"]},{"CurrentAttachment":"Simple Minimalist Business Invoice (1).pdf","ExtractionTime":"2025-08-05T15:59:02.4184036","FlaggedReason":["Error extractingPONo","Error extractingTax","Error extractingTotal"]}]'''

    # Log the inputs just like UiPath would
    log_uipath(extracted_json)
    log_uipath(purchase_order_json)
    log_uipath(flagged_json)

    # Run your validation
    out_extracted, out_flagged, out_successful = validate_invoices(
        extracted_json,
        purchase_order_json,
        flagged_json
    )

    # Log the outputs
    log_uipath(out_extracted)
    log_uipath(out_flagged)
    log_uipath(out_successful)
