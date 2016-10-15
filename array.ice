##
 # Arrays
##

def program
    set fruits Arr
    insert fruits "Grapefruit" "Apple" "Peach" "Pineapple" "Mango" "Melon"

    # SEEK method
    size $fruits len

    set i 0
    def loopa
        if $i < $len
            seek fruits $i fruit
            print "Item " $i ": " $fruit

            bit i + 1
            jump *loopa
        endif

    print

    # PUSH method
    push $fruits

    set i 0
    def loopb
        pop fruit

        if $fruit != $EMPTY
            print "Item " $i ": " $fruit

            bit i + 1
            jump *loopb
        endif

    exit
