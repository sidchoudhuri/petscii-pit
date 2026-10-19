; PETSCII Pit - Grand Medley demo, machine code version: loader
; LOAD"*",8 / RUN. Loads the medley for PAL or NTSC, the demo code and its
; data, then starts the demo at $0900. The one BASIC line is the usual
; "SYS 2061" start.

!cpu 6502
!source "build/consts.asm"
!to "build/pitmedley.prg", cbm

CHROUT = $ffd2
SETLFS = $ffba
SETNAM = $ffbd
LOAD   = $ffd5

* = $0801
        !word basend, 10
        !byte $9e
        !text "2061"
        !byte 0
basend  !word 0

start                           ; $080d
        lda #0
        sta $d020
        sta $d021
        ldx #0
-       lda msg,x
        beq +
        jsr CHROUT
        inx
        bne -
+       lda $ba                 ; the drive we were loaded from
        cmp #8
        bcs +
        lda #8
+       sta dev
        ldx #<npal              ; music for this machine
        ldy #>npal
        lda $02a6               ; 1 = PAL, 0 = NTSC
        beq +
        lda #npal_end-npal
        bne ++
+       ldx #<nntsc
        ldy #>nntsc
        lda #nntsc_end-nntsc
++      jsr loadfile
        ldx #<ncode
        ldy #>ncode
        lda #ncode_end-ncode
        jsr loadfile
        ldx #<nhi
        ldy #>nhi
        lda #nhi_end-nhi
        jsr loadfile
        ldx #<ndng
        ldy #>ndng
        lda #ndng_end-ndng
        jsr loadfile
        jmp ADDR_CODE

loadfile
        jsr SETNAM
        lda #1
        ldx dev
        ldy #1                  ; to the address in the file
        jsr SETLFS
        lda #0
        jsr LOAD
        bcs fail
        rts
fail    pla                     ; drop the return address
        pla
        ldx #0
-       lda errmsg,x
        beq +
        jsr CHROUT
        inx
        bne -
+       rts                     ; back to BASIC

dev     !byte 8
msg     !byte 147, 5
        !text "LOADING PETSCII PIT - GRAND MEDLEY ..."
        !byte 13, 0
errmsg  !text "LOAD ERROR"
        !byte 13, 0
npal    !text "MEDLEYPAL"
npal_end
nntsc   !text "MEDLEYNTSC"
nntsc_end
ncode   !text "DEMOCODE"
ncode_end
nhi     !text "DEMOHI"
nhi_end
ndng    !text "DEMODNG"
ndng_end
LOADER_END
!if LOADER_END > $08ff { !error "loader must stay below $0900" }
