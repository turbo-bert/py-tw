import tw

pdf = tw.DINA4()

# starting with page 1, not 0
pdf.page(1).text(1, 1, 'Hello World!')
pdf.build('output.pdf')
