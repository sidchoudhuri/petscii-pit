; PETSCII Pit level drawing helpers (V22), placed by the loader.
; FILL at $0720 (free once the loader's SID model check has run), REVEAL at
; $0576 (after the instructions routines at $0500). The tables are filled by
; the game from its own glyph and colour constants.
; Zero page $57-$5F (free during a SYS; the music IRQ uses $FB/$FC).
;
; SYS 1824 FILL:   draw every map cell (rows 3-24) on the $C000 screen from
;                  the MA% array, in black, so nothing shows until revealed.
; SYS 1398 REVEAL: for a rectangle (start cell, width, height), set the fog
;                  bytes at $C400 to 1 and colour each cell by its character
;                  from the colour list. Characters not in the list (the
;                  player, a monster) keep their colour.

NP      = 13

src     = $57           ; MA% data pointer / fog pointer
scr     = $59           ; screen pointer
col     = $5b           ; colour pointer
cnt     = $5d           ; cells left (16 bit)
tmp     = $5f

        * = $0720

; ---- FILL ----
; find the integer array MA% ("M"+$80, "A"+$80) between ($2F) and ($31)
fill    lda $2f
        sta src
        lda $30
        sta src+1
find    lda src+1
        cmp $32
        bcc +
        bne nofind
        lda src
        cmp $31
        bcs nofind
+       ldy #0
        lda (src),y
        cmp #$cd
        bne next
        iny
        lda (src),y
        cmp #$c1
        beq found
next    ldy #2
        lda (src),y
        clc
        adc src
        tax
        iny
        lda (src),y
        adc src+1
        sta src+1
        stx src
        jmp find
nofind  rts
; data starts 7 bytes in (name 2, size 2, dims 1, dim size 2); skip to cell 120
found   lda src
        clc
        adc #7+240
        sta src
        lda src+1
        adc #0
        sta src+1
        lda #<($c000+120)
        sta scr
        sta col
        lda #>($c000+120)
        sta scr+1
        lda #>($d800+120)
        sta col+1
cell    ldy #0
        lda (src),y     ; high byte
        sta tmp
        iny
        lda (src),y     ; low byte
        ldx tmp
        bne weap
        cmp #20
        bcs weap
        tax
        lda ctab,x
        jmp put
; weapon: (T-20) mod 10 = WT-1
weap    sec
        sbc #20
        tax
        lda tmp
        sbc #0
        sta tmp
        txa
-       ldx tmp
        bne +
        cmp #10
        bcc ++
+       sec
        sbc #10
        bcs -
        dec tmp
        jmp -
++      cmp #5
        bcs blank
        tax
        lda wtab,x
        jmp put
blank   lda #32
put     ldy #0
        sta (scr),y
        tya
        sta (col),y
        lda src
        clc
        adc #2
        sta src
        bcc +
        inc src+1
+       inc scr
        bne +
        inc scr+1
+       inc col
        bne +
        inc col+1
+       lda scr
        cmp #$e8
        bne cell
        lda scr+1
        cmp #$c3
        bne cell
        rts
ctab    !fill 20,32     ; character for MA% 0-19
wtab    !fill 5,32      ; weapon characters, WT 1-5
endb

; ---- REVEAL (SYS 1398) ----
        * = $0576
reveal  lda rlo
        sta scr
        sta col
        sta src
        lda rhi
        clc
        adc #$c0
        sta scr+1
        adc #$04
        sta src+1       ; fog $C400
        adc #$14
        sta col+1       ; colour $D800
        lda rh
        sta cnt
row     ldy #0
rcell   lda #1
        sta (src),y
        lda (scr),y
        ldx #NP-1
-       cmp pchr,x
        beq +
        dex
        bpl -
        jmp rnext
+       lda pcol,x
        sta (col),y
rnext   iny
        cpy rw
        bne rcell
        ldx #src
        jsr add40
        ldx #scr
        jsr add40
        ldx #col
        jsr add40
        dec cnt
        bne row
        rts
add40   lda 0,x
        clc
        adc #40
        sta 0,x
        bcc +
        inc 1,x
+       rts
pchr    !fill NP,0      ; colour list characters
pcol    !fill NP,0      ; colour list colours
rlo     !byte 0         ; start cell low
rhi     !byte 0         ; start cell high
rw      !byte 0         ; width
rh      !byte 0         ; height
enda
