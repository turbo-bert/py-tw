import tw

pdf = tw.DINA3()
pdf.page(1).text(1,1,"1/1")
pdf.build('example3.pdf')
