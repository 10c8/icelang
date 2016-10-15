##
 # Structs demonstration
##

# typedef Person
struct Person
    field name Str
    field age Int

def program
    # Create an instance of type Person
    set emma @Person
        set #name "Emma"
        set #age 19

    # Push all instances of Person to the stack
    push @Person

    def main
        # Pop an instance from the stack to "current"
        pop current

        if $current == $EMPTY
            # End of the stack
            call *end
        else
            with $current
                print #name ", " #age " years."

            jump *main
        endif

def end
    exit
