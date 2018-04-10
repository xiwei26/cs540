This goes at line 157 in the processFile() method.
It will allow us to pass over a blank line in the input file.
--There is obvious overlap in this fix to help align the fix 

## To handle extra spaces in a line of text
            ind = 0
            hold = 0
            sizeVals = len(values)
            if sizeVals < 4:
                print("A line of text is incomplete, skipping:", values)
                continue
            if sizeVals > 4:
