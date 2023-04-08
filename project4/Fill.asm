// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.

(TESTKEY)
    // check if a key is being pressed
    @KBD
    D = M
    // if M is 0 (no press) then white the screen, otherwise - black 
    @NOPRESS
    D;JEQ 

    // if pressed then we got here so we need to set all pixeles to one and blacken the screen
    @8191 // 8192 lines representing the pixeles
    D = A
    @row // creating new variable that will point on current row we want to color (in the block of screen memory)
    M = D
    (LOOPBLACK)
        @row
        D = M
        @TESTKEY 
        D;JLT // if all the pixeles are set to zero then check again if a key is being pressed 
        @row 
        D = M
        @SCREEN
        A = D + A
        M = -1
        @row 
        M = M - 1
        @LOOPBLACK
        0;JMP

    (NOPRESS) // if no key is pressed, turning all the pixels to white
        @8191 // 8192 lines representing the pixeles
        D = A
        @row // creating new variable that will point on current row we want to color (in the loop)
        M = D
        (LOOPWHITE)
            @row
            D = M
            @TESTKEY 
            D;JLT // if all the pixeles are set to zero then check again if a key is being pressed
            @row 
            D = M
            @SCREEN
            A = D + A
            M = 0
            @row 
            M = M - 1
            @LOOPWHITE
            0;JMP


    