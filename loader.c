/* 
    Loader Assignment
    // Saleh Alammar           362118497
    // Mohammad Marwan         362118614
    // Abdulaziz Almohaimeed   351108841
*/
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

int main()
{
    FILE *fp = fopen("output.obj", "r");
    int *mm = malloc((int)pow(2, 20));
    srand(time(NULL));
    int pm, prog_size, start_addr;
    char record = fgetc(fp);
    while (record != 'E')
    {
        if (record == 'H')
        {
            char prog_name[100];
            fscanf(fp, "%s %x %x", prog_name, &start_addr, &prog_size);
            pm = rand() % ((int)pow(2, 20) - prog_size);
        }

        else if (record == 'T')
        {
            int addr, ln_size, ptr = 0;
            fscanf(fp, "%x %x", &addr, &ln_size);
            for (int i = 0; i < ln_size; i++)
            {
                int byte;
                fscanf(fp, "%2x", &byte);
                *(mm + pm + ptr++ + addr) = byte;
            }
        }
        record = fgetc(fp);
    }

    // // FOR TESTING
    // // Prints data in the memory
    // for (int i = 0; i < prog_size; i++)
    // {
    //     printf("%3x ", *(mm + pm + start_addr + i));
    //     if (i % 3 == 2)
    //     {
    //         printf("\n");
    //     }
    // }
}

/*
// INPUT WE USED 

H CPYS 000064 000026
T 000064 03 072003
T 000067 03 53A00C
T 00006a 03 616263
T 00006d 03 57A00D
T 000070 03 2F2F94
T 000073 03 3B2FF1
T 00007A 07 50726F6A656374
T 000084 03 000007
T 000087 03 000001
E 000064

*/
