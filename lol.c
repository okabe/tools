#include <linux/module.h>
#include <linux/init.h>
#include <linux/types.h>
#include <asm/uaccess.h>
#include <asm/cacheflush.h>
#include <linux/syscalls.h>
#include <linux/delay.h>

#define CR0_WP 0x00010000

MODULE_LICENSE( "GPL" );

void **syscall_table;
unsigned long **find_sys_call_table( void );

long ( *orig_sys_open )( const char __user *filename, int flags, int mode );

/*
 * unsigned long **find_sys_call_table() {
 *    unsigned long ptr;
 *    unsigned long *p;
 * 
 *    for( ptr = ( unsigned long )rt_retcode;
 *         ptr < ( unsigned long )&print_trace_ops;
 *         ptr += sizeof( void * )) {
 *        
 *        p = ( unsigned long * )ptr;
 *        if ( p[__NR_close] == ( unsigned long )sys_close ) {
 *            printk( KERN_INFO "Found the sys_call_table!!!\n" );
 *            return ( unsigned long ** )p;
 *        }
 *    }
 *    return NULL;
 * }
 */


/* patch sys_open to enable kernel alerting */
long my_sys_open( const char __user *filename, int flags, int mode ) {
    long ret;
    
    ret = orig_sys_open( filename, flags, mode );
    printk( KERN_INFO "[+] File %s was opened with mode %d\n", filename, mode );

    return ret;
}

/* entry point: onload locate sys_call_table and patch sys_open */
static int __init syscall_init( void ){
    int ret;
    unsigned long addr;
    unsigned long cr0;

    /* need to figure out how to pass in the memory address of sys_call_table, hard code for now */

    syscall_table = ( void *)0xc12cde90;

    if ( !syscall_table ){
        printk( KERN_INFO "[!] Failed to locate sys_call_table\n" );
        return -1;
    }

    /* flip the write protection bit off in the control register */
    cr0 = read_cr0();
    write_cr0( cr0 & ~CR0_WP );

    addr = ( unsigned long )syscall_table;
    ret = set_memory_rw( PAGE_ALIGN( addr ) - PAGE_SIZE, 3 );

    if( ret ){
        printk( 
            KERN_INFO "[!] Failed to set the memory to rw (%d) at addr %16lX\n", 
            ret, PAGE_ALIGN( addr ) - PAGE_SIZE 
        );
    } else {
        printk( KERN_INFO "[+] 3 pages set to rw" );
    }

    orig_sys_open = syscall_table[__NR_open];
    syscall_table[__NR_open] = my_sys_open;

    write_cr0( cr0 );

    return 0;
}

/* clean up before unloading */
static void __exit syscall_release( void ){
    unsigned long cr0;
    cr0 = read_cr0();
    write_cr0( cr0 & ~CR0_WP );

    syscall_table[__NR_open] = orig_sys_open;

    write_cr0( cr0 );
}

module_init( syscall_init );
module_exit( syscall_release );
