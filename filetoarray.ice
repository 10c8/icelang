##
 # Read a file to an Array, then print it with line numbers
##

def program
    set file %File
    set lines Arr

    fread file "test.txt"
    size %file len

    set i 0
    def readline
        if $i < $len
            frseek %file $i line
            insert lines $line

            bit i + 1
            jump *readline
        endif

    size $lines len

    set i 0
    def show
        if $i < $len
            seek lines $i line

            bit i + 1
            print $i "| " $line

            jump *show
        endif

    exit
