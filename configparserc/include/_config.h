#include <string.h>
#include <ctype.h>

#ifdef __GLIBC__
__asm__(".symver strlen,strlen@GLIBC_2.2.5");
__asm__(".symver memcpy,memcpy@GLIBC_2.2.5");
__asm__(".symver free,free@GLIBC_2.2.5");
__asm__(".symver isspace,isspace@GLIBC_2.2.5");
__asm__(".symver fmemopen,fmemopen@GLIBC_2.2.5");
#endif

int __has_only_whitespaces(char* s) {
    unsigned int i;
    for (i = 0; i < strlen(s); i++) {
        if (isspace(s[i]) == 0){
            return 0;
        }
    }
    return 1;
}
