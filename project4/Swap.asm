// This file is part of nand2tetris, as taught in The Hebrew University, and
// was written by Aviv Yaish. It is an extension to the specifications given
// [here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
// as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
// Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).

// The program should swap between the max. and min. elements of an array.
// Assumptions:
// - The array's start address is stored in R14, and R15 contains its length
// - Each array value x is between -16384 < x < 16384
// - The address in R14 is at least >= 2048
// - R14 + R15 <= 16383
//
// Requirements:
// - Changing R14, R15 is not allowed.

// Put your code here.

// going through all the array and finding the min and max items, and saving the address to them 

// getting the address of the first value and putting it as the address of min and max
@R14
D = M // now D is the address of arr[0]
@cur_address // keeping the current address
M = D - 1 // - 1 because in the loop first advencing the address
@max_address // keeping the address of the max value and initialized with the address of arr[0]
M = D
@min_address // keeping the address of min value and initialized with the address of arr[0]
M = D

// putting the first value as max and min 
@R14
A = M // now address is of arr[0]
D = M // D == arr[0] (value)
@max_val // keeping the max value
M = D
@min_val // keeping the min value
M = D

// arranging the number of loops needed to be done
@R15
D = M
@loops_to_do
M = D + 1

// checking if a[i] is bigger then max - if it does, replace it with max 
(LOOP_MAX) // entring with i-1 and the current loop runs on i
    // cheking if loop need to end
    @loops_to_do // how many loops left
    MD = M - 1
    @INIT_FOR_LOOP_MIN // goto next part of the code (after this loop) if D <= 0 
    D;JLE // when it's zero (or less), it means we should stop looping because we reached the end of the array

    @cur_address // the cuurent address
    AM = M + 1 // advencing 
    D = M // D == a[i]
    @max_val
    D = M - D // max - a[i]
    @LOOP_MAX
    D;JGE // if LT - max - a[i] < 0 then need to replace max, otherwise continue looping
    // replace a[i] with max - first address replacement and then value replacement
    @cur_address
    A = M
    D = M
    @max_val
    M = D

    @cur_address
    D = M
    @max_address
    M = D

    @LOOP_MAX
    0;JMP

(INIT_FOR_LOOP_MIN) // chek this
// initializing cur_address to arr[0] address 
@R14
D = M // now D is the address of arr[0]
@cur_address // keeping the current address
M = D - 1 // - 1 because in the loop first advencing the address

// arranging the number of loops needed to be done
@R15
D = M
@loops_to_do
M = D + 1

// checking if a[i] is smaller then min - if it does, replace it with min 
(LOOP_MIN)
    // cheking if loop need to end
    @loops_to_do // how many loops left
    MD = M - 1
    @REPLACE_MIN_AND_MAX
    D;JLE // when it's zero (or less), it means we should stop looping because we reached the end of the array

    @cur_address // the cuurent address
    AM = M + 1 // advencing 
    D = M // D == a[i]
    @min_val
    D = M - D // min - a[i] <= 0   <->    min <= a[i]   <-> no need to replace
    @LOOP_MIN
    D;JLE // if GT - min - a[i] > 0 then need to replace min with a[i], otherwise continue looping
    // replace a[i] with min - first address replacement and then value replacement
    @cur_address
    A = M
    D = M
    @min_val
    M = D

    @cur_address
    D = M
    @min_address
    M = D

    @LOOP_MAX
    0;JMP

(REPLACE_MIN_AND_MAX)
@min_val
D = M
@temp_min
M = D

@max_val
D = M
@min_address
A = M
M = D // change min value to max value

@temp_min
D = M
@max_address
A = M
M = D // change max value to min value


(END_OF_PROGRAM)
    @END_OF_PROGRAM
    0;JMP