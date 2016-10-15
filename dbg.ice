##
 # ICE Input Test
##

def program
    print "What is your name?"

    print "> ",
    input name Str

    print "Hello, " $name "! In what year were you born?"

    print "> ",
    input year Int

    set currentYear 2016
    bit currentYear - $year
    set age $currentYear

    if $age > 150
        print "Are you sure?"
        jump *program
    elif $age >= 18
        set title "adult"
    elif $age >= 15 and $age < 18
        set title "teenager"
    elif $age >= 12 and $age < 15
        set title "pre-teen"
    else
        set title "child"
    endif

    print "So you're " $age " years old! A(n) " $title "!"

    exit
