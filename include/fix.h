#ifdef BUILD_FROM_SOURCE
#else
#ifdef __GLIBC__

__asm__(".symver strlen,strlen@GLIBC_2.2.5");
__asm__(".symver memcpy,memcpy@GLIBC_2.2.5");
__asm__(".symver free,free@GLIBC_2.2.5");
__asm__(".symver isspace,isspace@GLIBC_2.2.5");
__asm__(".symver fmemopen,fmemopen@GLIBC_2.2.5");

#endif
#endif
