#include <stdlib.h>
#include <stdio.h>

int main()
{
    FILE *fp = fopen("output.obj", "r");
    int *mm, *ptr;
    char record = fgetc(fp);
    while (record != 'E')
    {
        if (record == 'H')
        {
            char prog_name[100];
            int start_addr, prog_size;
            fscanf(fp, "%s %x %x", prog_name, &start_addr, &prog_size);
            ptr = mm = malloc(prog_size);
        }

        else if (record == 'T')
        {
            int code_addr, ln_size;
            fscanf(fp, "%x %x", &code_addr, &ln_size);
            for (int i = 0; i < ln_size; i++)
            {
                int byte;
                fscanf(fp, "%2x", &byte);
                *ptr++ = byte;
            }
        }
        record = fgetc(fp);
    }
}