import tw

pdf = tw.DINA3()


#pdf.page(1).text(1,1,"1")

#wx=137
#pdf.page(1).text(1,wx,"|")
#pdf.page(1).text(1,wx-20,"%d ---> " % wx)
#
#pdf.page(1).text(103,1,"103")

cols=[1,10,20,30,40,50,60,70,80,90,100,110,120,130]
for col in cols:
    for row in range(1,103+1):
        pdf.page(1).text(row, col,"|")

for row in range(1,103+1):
    for col in cols:
        if col > 1 and row > 1 and row%5==0:
            pdf.page(1).text(row, col+1,"%d"%col)
            pdf.page(1).text(row-1, col+1,"|")

for row in range(1,103+1):
    if row == 1 or row % 5 == 0:
        pdf.page(1).text(row, 1, "_"*136)
        pdf.page(1).text(row, 4, "%d" % row)
        pdf.page(1).text(row-1, 4, "_")



pdf.build('DINA3_Ruler.pdf')
