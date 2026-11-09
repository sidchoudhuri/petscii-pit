; PETSCII Pit screen transitions, placed by the loader at $0600 (the unused
; default screen memory), with the per-cell code and a page copy at $9500
; (the old colour save/restore, unused since V20).
; Ops 0/1 change colour memory only; ops 2/3 also write the screen in scrp.
; Zero page $57-$5E (free during a SYS; the music IRQ uses $FB/$FC).
; Buffers live in the RAM under the BASIC ROM ($A000 map colours, $A400
; battle colours, $A800 map characters, $AC00 battle characters), read with
; $01=$36 so the KERNAL and its IRQ stay in.
        * = $0600
kind    !byte 0         ; 1536: 0 rows, 1 columns, 2 shutter (rows from top and bottom)
rev     !byte 0         ; 1537: 0 forward (top->bottom, left->right, outside->middle), 1 reverse
op      !byte 0         ; 1538: 0 to black, 1 copy colours, 2 red blocks, 3 copy characters and colours
srch    !byte $a0       ; 1539: buffer page ($A0 or $A4)
per     !byte 5         ; 1540: rows/columns per frame
; SYS 1541: save colour memory to the buffer page in srch
save    lda srch
        sta $5a
        lda #$d8
        sta $58
        lda #0
        sta $57
        sta $59
        ldx #4
        ldy #0
-       lda ($57),y
        sta ($59),y
        iny
        bne -
        inc $58
        inc $5a
        dex
        bne -
        rts
; SYS fx: run the transition
fx      lda #$36
        sta $01
        lda #0
        sta i
        ldx kind
        lda nt,x
        sta n
frame   lda per
        sta cnt
unit    lda i
        ldy rev
        beq +
        lda n
        clc
        sbc i           ; n-1-i
+       sta u
        ldx kind
        beq dorow
        dex
        beq docol
        lda u           ; shutter: row u and row 24-u
        jsr row
        lda #24
        sec
        sbc u
        jsr row
        jmp next
dorow   lda u
        jsr row
        jmp next
docol   lda u
        sta $57
        lda #0
        sta $58
        lda #25
        ldx #40
        jsr run
next    inc i
        lda i
        cmp n
        beq done
        dec cnt
        bne unit
-       lda $d012       ; wait for the next frame (raster lines 250-255)
        cmp #$fa
        bcs -
-       lda $d012
        cmp #$fa
        bcc -
        jmp frame
done    lda #$37
        sta $01
        rts
row     sta t           ; offset = A*40, 40 cells, stride 1
        lda #0
        sta $58
        lda t
        asl
        asl
        asl
        sta t8
        asl
        rol $58
        asl
        rol $58
        clc
        adc t8
        sta $57
        bcc +
        inc $58
+       lda #40
        ldx #1
        jmp run
nt      !byte 25,40,13
i       !byte 0
n       !byte 0
cnt     !byte 0
u       !byte 0
t       !byte 0
t8      !byte 0
; per cell (entered from run at $9500)
cell    lda op
        beq o0
        cmp #2
        bcc o1
        beq o2
        lda ($5d),y     ; 3: character and colour from the buffers
        sta ($5b),y
o1      lda ($59),y
        bcs st          ; (op 3 arrives with carry set)
        bcc st
o2      lda #160        ; 2: red reverse space
        sta ($5b),y
        lda #2
        bne st
o0      lda #0
st      sta ($57),y
        ldx #6
-       lda $57,x
        clc
        adc s
        sta $57,x
        bcc +
        inc $58,x
+       dex
        dex
        bpl -
        dec c
        bne cell
        rts
endlow

; ---- $9500: per-cell code ----
        * = $9500
; $57/$58 = cell offset, A = count, X = stride
run     sta c
        stx s
        lda $57
        sta $59
        sta $5b
        sta $5d
        ldx $58
        txa
        clc
        adc srch
        sta $5a
        txa
        adc scrp
        sta $5c
        txa
        adc chrb
        sta $5e
        txa
        adc #$d8
        sta $58
        ldy #0
        jmp cell
endrun

; ---- $95CD (38349): settings and a 1 KB copy ----
        * = $95cd
scrp    !byte $c0       ; 38349: screen page for ops 2/3 ($C0 map, $E8 battle)
chrb    !byte $a8       ; 38350: character buffer page ($A8 map, $AC battle)
cfrom   !byte $c0       ; 38351: SYS 38355 copies 4 pages from this page...
cto     !byte $a8       ; 38352: ...to this one (KERNAL and BASIC switched out)
c       !byte 0
s       !byte 0
        !byte 0
copy    sei
        lda #$35
        sta $01
        lda cfrom
        sta $58
        lda cto
        sta $5a
        lda #0
        sta $57
        sta $59
        ldx #4
        tay
-       lda ($57),y
        sta ($59),y
        iny
        bne -
        inc $58
        inc $5a
        dex
        bne -
        lda #$37
        sta $01
        cli
        rts
endhi
