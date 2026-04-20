

from fpdf import FPDF 

from fpdf import FPDF 

def create_dummy_invoice ():
    pdf =FPDF ()
    pdf .add_page ()
    pdf .set_font ("Arial",size =12 )

    pdf .set_font ("Arial",style ="B",size =16 )
    pdf .cell (200 ,10 ,txt ="TAX INVOICE",ln =True ,align ="C")
    pdf .set_font ("Arial",size =12 )
    pdf .cell (200 ,10 ,txt ="Invoice Number: INV-IND-2026-090",ln =True ,align ="R")
    pdf .cell (200 ,10 ,txt ="Date Issued: April 7, 2026",ln =True ,align ="R")
    pdf .ln (10 )

    pdf .set_font ("Arial",style ="B",size =12 )
    pdf .cell (100 ,10 ,txt ="From: Cloud Data Dynamics Pvt Ltd",ln =False )
    pdf .cell (100 ,10 ,txt ="Billed To: Robin Singh",ln =True )
    pdf .set_font ("Arial",size =12 )
    pdf .cell (100 ,10 ,txt ="GSTIN: 09AAACA1234Z1Z5",ln =False )
    pdf .cell (100 ,10 ,txt ="GSTIN: 09BBBCB5678Y2Y6",ln =True )
    pdf .ln (10 )

    pdf .set_font ("Arial",style ="B",size =12 )
    pdf .cell (100 ,10 ,txt ="Description",border =1 )
    pdf .cell (30 ,10 ,txt ="Qty",border =1 ,align ="C")
    pdf .cell (30 ,10 ,txt ="Unit Price",border =1 ,align ="C")
    pdf .cell (30 ,10 ,txt ="Amount",border =1 ,align ="C")
    pdf .ln (10 )

    pdf .set_font ("Arial",size =12 )

    pdf .cell (100 ,10 ,txt ="Cloud Server Hosting (SaaS)",border =1 )
    pdf .cell (30 ,10 ,txt ="1",border =1 ,align ="C")
    pdf .cell (30 ,10 ,txt ="100000.00",border =1 ,align ="C")
    pdf .cell (30 ,10 ,txt ="100000.00",border =1 ,align ="C")
    pdf .ln (10 )

    subtotal =100000.00 
    gst =18000.00 
    total =118000.00 

    pdf .ln (5 )
    pdf .cell (160 ,10 ,txt ="Subtotal:",align ="R")
    pdf .cell (30 ,10 ,txt =str (subtotal ),ln =True ,align ="C")

    pdf .cell (160 ,10 ,txt ="GST Applied (18%):",align ="R")
    pdf .cell (30 ,10 ,txt =str (gst ),ln =True ,align ="C")

    pdf .set_font ("Arial",style ="B",size =12 )
    pdf .cell (160 ,10 ,txt ="Total (INR):",align ="R")
    pdf .cell (30 ,10 ,txt =str (total ),ln =True ,align ="C")

    pdf .output ("invoice_with_tax.pdf")
    print ("invoice_with_tax.pdf generated successfully!")

if __name__ =="__main__":
    create_dummy_invoice ()