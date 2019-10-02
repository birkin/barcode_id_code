### About

This is reference code to remind myself in the future of a lightweight way of experimenting.

More specifically about this code...

I have a plan to convert automated Sierra requests to use the Sierra APIs instead of an old existing method of mimic-ing a patron-barcode & name login to the old OPAC.

For this I need to convert the patron-barcode I have access to, to a sierra-patron-id. And for that I plan to use Sierra's patron-api, which takes a barcode and returns back various info.

So, to test, I went through some log-files, pulled out some patron-barcodes and performed a lookup on them, mostly to check that all the barcodes did, in fact, have an id.

---
