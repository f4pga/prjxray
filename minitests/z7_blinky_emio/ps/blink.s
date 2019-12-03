@ https://craigjb.com/2019/03/04/zynq-baremetal-blinky/

@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@ Constants

.equ C_GPIO_BASE,           0xE000A000
.equ C_GPIO_DIRM_0,         0x00000204
.equ C_GPIO_OEN_0,          0x00000208
.equ C_GPIO_DATA_0,         0x00000040
.equ C_GPIO_DIRM_2,         0x00000284
.equ C_GPIO_OEN_2,          0x00000288
.equ C_GPIO_DATA_2,         0x00000048

.equ C_SLCR_BASE,           0xF8000000
.equ C_SLCR_UNLOCK,         0x00000008
.equ C_SLCR_LOCK,           0x00000004
.equ C_SLCR_MIO_PIN_07,     0x0000071C
.equ C_SLCR_LVL_SHFTR_EN,   0x00000900
.equ C_SLCR_LOCK_KEY,       0x767B
.equ C_SLCR_UNLOCK_KEY,     0xDF0D

.equ C_DELAY,               0x00200000


@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@ Vector table

.section .text
.code 32
.globl vectors
vectors:
    b entry         @ reset
    b .             @ undefined instruction
    b .             @ software interrupt
    b .             @ prefetch abort
    b .             @ data abort
    b .             @ hypervisor entry
    b .             @ interrupt
    b .             @ fast interrupt

@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@ The code

entry:
    @ unlock SLCR
    ldr r0, SLCR_BASE
    ldr r1, SLCR_UNLOCK_KEY
    str r1, [r0, #C_SLCR_UNLOCK]

    @ setup MIO pin, LVCMO33 and no tri-state
    mov r1, #0x600
    str r1, [r0, #C_SLCR_MIO_PIN_07]

    @ enable level shifters on PS-PL interface
    mov r1, #0xF
    str r1, [r0, #C_SLCR_LVL_SHFTR_EN]

    @ lock SLCR
    ldr r1, SLCR_LOCK_KEY
    str r1, [r0, #C_SLCR_LOCK]

    @ setup GPIO0 dir, output en, and data
    ldr r0, GPIO_BASE
    mov r1, #0x80
    str r1, [r0, #C_GPIO_DIRM_0]
    str r1, [r0, #C_GPIO_OEN_0]
    str r1, [r0, #C_GPIO_DATA_0]
    mov r1, #0x0F
    str r1, [r0, #C_GPIO_DIRM_2]
    str r1, [r0, #C_GPIO_OEN_2]
    mov r1, #0x00
    str r1, [r0, #C_GPIO_DATA_2]

    mov r4, #0x00

loop_outer:
    mov r3, #C_DELAY

loop0:
    subs r3, r3, #1
    bne loop0

    mov r1, #0x80
    str r1, [r0, #C_GPIO_DATA_0]

    mov r3, #C_DELAY
loop1:
    subs r3, r3, #1
    bne loop1

    mov r1, #0x00
    str r1, [r0, #C_GPIO_DATA_0]

    add r4, r4, #1
    str r4, [r0, #C_GPIO_DATA_2]

    b loop_outer


    b .  @ just in case

@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@ Literal table

GPIO_BASE:       .word C_GPIO_BASE
SLCR_BASE:       .word C_SLCR_BASE
SLCR_LOCK_KEY:   .word C_SLCR_LOCK_KEY
SLCR_UNLOCK_KEY: .word C_SLCR_UNLOCK_KEY
