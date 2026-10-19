; PETSCII Pit - Grand Medley demo, by m0nde
; machine code part (ACME). Loaded and started by the BASIC shell (SYS 2560).
;
; screen layout
;   row 0      title / author / date, scrolling left to right
;   rows 1-22  dancers (2.5x quarter blocks) with name labels, then the
;              portrait ending, two small dancer bands and the dungeon strip
;              (rows 9-14, game font from $0800)
;   row 23     blank buffer row
;   row 24     greetings, scrolling right to left
;
; raster IRQs (KERNAL and BASIC switched out, own vectors at $FFFE)
;   A  line 10   top row scroll value, text scrollers, frame logic
;   B  line 56   middle scroll value at the end of line 58, music
;   D  line 120  dungeon font on from row 9      (only while the dungeon runs)
;   E  line 168  ROM font back from row 15
;   C  line 238  bottom row scroll value (inside the blank buffer row)
;
; the main loop draws the middle rows when the IRQ asks for it, always
; behind the raster beam, so nothing tears.

!cpu 6502
!source "build/consts.asm"
!to "build/democode.prg", cbm

MUSIC_INIT = $9300
MUSIC_PLAY = $9703
SCREEN     = $0400
COLRAM     = $d800
ROWSIZE    = 40*7+1             ; one row of the unrolled draw code

; zero page (the music uses $fb/$fc and $033c-, the rest is ours)
srcp    = $02                   ; draw source pointer
dstp    = $04                   ; main loop destination pointer
recp    = $06                   ; next shrink frame record
topp    = $08                   ; top text pointer
botp    = $0a                   ; bottom text pointer
fcnt    = $0c                   ; music frames played (2 bytes)
songend = $0e                   ; frame where the medley ends (2 bytes)
o       = $10                   ; fine scroll step 0-7
mode    = $11                   ; 0 dancers, 1 portrait in, 2 colour wipe,
                                ; 3 shrink, 4 pause, 5 small dancer bands
pos     = $12                   ; big strip column
ph      = $13                   ; big dance phase 0-3
wraps   = $14
tstep   = $15                   ; portrait columns entered (0-40)
req     = $16                   ; draw request: 1 big, 2 shrink, 3 small, 4 colours
xstop   = $17
xsmid   = $18
xsbot   = $19
timer   = $1a
wrow    = $1b                   ; colour wipe row
posa    = $1c                   ; small band A column (moves left)
posb    = $1d                   ; small band B column (moves right)
sph     = $1e                   ; small dance phase
sstep   = $1f
lpos    = $20                   ; values latched for the main loop
lph     = $21
lt      = $22
rowi    = $23
tmp     = $24
cols    = $25
rows    = $26
vec     = $27                   ; 2 bytes
lsph    = $29
lposa   = $2a
lposb   = $2b
ltmp    = $2c
idstp   = $2e                   ; IRQ destination pointer (2 bytes)
patch   = $30                   ; row code byte patched with RTS (2 bytes)
patchv  = $32
dng     = $33                   ; dungeon running
dptr    = $34                   ; dungeon stream pointer (2 bytes)
dgl     = $36
dcnt    = $37
DFONT   = $0800                 ; dungeon glyphs (screen codes 0-21)

* = ADDR_CODE

start
        sei
        lda #$7f
        sta $dc0d               ; no CIA interrupts
        sta $dd0d
        lda $dc0d
        lda $dd0d
        lda #$35                ; RAM everywhere except I/O
        sta $01
        ldx #DFONT_LEN-1        ; dungeon glyphs (the loader is done with $0800)
-       lda ADDR_DFONT,x
        sta DFONT,x
        dex
        cpx #$ff
        bne -
        lda #<nmi
        sta $fffa
        lda #>nmi
        sta $fffb
        lda #0
        sta $d020
        sta $d021
        sta $d015
        lda #$14                ; screen $0400, uppercase/graphics font
        sta $d018
        lda #$1b
        sta $d011
        lda #$07                ; 38 columns, scroll 7
        sta $d016

        ldx #0                  ; clear the screen, colour white
-       lda #SPACE
        sta SCREEN,x
        sta SCREEN+$100,x
        sta SCREEN+$200,x
        sta SCREEN+$2e8,x
        lda #1
        sta COLRAM,x
        sta COLRAM+$100,x
        sta COLRAM+$200,x
        sta COLRAM+$2e8,x
        inx
        bne -

        ldx #1                  ; dancer rows shade white to dark grey
-       lda bigcol-1,x
        jsr setrowcol
        inx
        cpx #23
        bne -
        ldx #24                 ; greetings row light grey
        lda #15
        jsr setrowcol

        ldx #$36                ; clear our zero page
        lda #0
-       sta $02,x
        dex
        bpl -
        lda #7
        sta o
        lda #<ADDR_TOP
        sta topp
        lda #>ADDR_TOP
        sta topp+1
        lda #<ADDR_BOT
        sta botp
        lda #>ADDR_BOT
        sta botp+1
        lda #<SONG_PAL
        ldx #>SONG_PAL
        ldy $02a6               ; 1 = PAL, 0 = NTSC
        bne +
        lda #<SONG_NTSC
        ldx #>SONG_NTSC
+       sta songend
        stx songend+1

        lda #0
        jsr MUSIC_INIT

        lda #<irqa
        sta $fffe
        lda #>irqa
        sta $ffff
        lda #10
        sta $d012
        lda #$1b
        sta $d011
        lda #1
        sta $d01a
        lda #$ff
        sta $d019
        cli

; ------------------------------------------------------------ main loop
mainloop
        lda req
        beq mainloop
        cmp #1
        beq dobig
        cmp #2
        bne +
        jmp doshrink
+       cmp #3
        bne +
        jmp dosmall
+       cmp #4
        bne +
        jmp docolours
+       jmp dodclear
done
        lda #0
        sta req
        jmp mainloop

; wait until the raster is at line A or a little past it
waitline
        sta ltmp
-       lda $d011
        bmi -
        lda $d012
        cmp ltmp
        bcc -
        sec
        sbc ltmp
        cmp #80
        bcs -
        rts

; ---------------------------------------------- big dancers (and portrait)
dobig
        lda #100
        jsr waitline
        lda #0
        sta rowi
bigrow
        ldx lph
        lda ph23,x
        clc
        adc rowi
        tax
        lda bigrowlo,x
        clc
        adc lpos
        sta srcp
        lda bigrowhi,x
        adc #0
        sta srcp+1
        ldx rowi
        lda lt
        bne +
        jsr callrow             ; whole row from the dancer strip
        jmp nextbig
+                               ; portrait coming in: dancers in columns
        lda #40                 ; 0 to s-1, portrait strip from s to 39
        sec
        sbc lt
        sta tmp                 ; s
        tay
        lda rowcodelo,x         ; put an RTS at column s
        clc
        adc mul7lo,y
        sta patch
        lda rowcodehi,x
        adc mul7hi,y
        sta patch+1
        ldy #0
        lda (patch),y
        sta patchv
        lda #$60
        sta (patch),y
        jsr callrow
        ldy #0                  ; put the row code back
        lda patchv
        sta (patch),y
        ldx rowi
        lda outrolo,x           ; portrait strip, index from column s
        sec
        sbc tmp
        sta srcp
        lda outrohi,x
        sbc #0
        sta srcp+1
        lda tmp
        jsr callrowat
nextbig
        inc rowi
        lda rowi
        cmp #23                 ; 22 screen rows + the label colours of row 21
        bne bigrow
        jmp done

; call row code X (screen row X+1) from column 0, or from column A
callrow
        lda #0
callrowat
        tay
        lda rowcodelo,x
        clc
        adc mul7lo,y
        sta vec
        lda rowcodehi,x
        adc mul7hi,y
        sta vec+1
        jmp (vec)

; ---------------------------------------------------- portrait shrinking
doshrink
        lda #200
        jsr waitline
        ldy #0
        lda (recp),y
        tax                     ; screen row
        iny
        lda (recp),y
        sta tmp                 ; column
        iny
        lda (recp),y
        sta rows
        iny
        lda (recp),y
        sta cols
        lda rowlo,x
        clc
        adc tmp
        sta dstp
        lda rowhi,x
        adc #0
        sta dstp+1
        lda recp
        clc
        adc #4
        sta recp
        bcc srow
        inc recp+1
srow
        ldy cols
        dey
-       lda (recp),y
        sta (dstp),y
        dey
        bpl -
        lda recp
        clc
        adc cols
        sta recp
        bcc +
        inc recp+1
+       lda dstp
        clc
        adc #40
        sta dstp
        bcc +
        inc dstp+1
+       dec rows
        bne srow
        jmp done

; ------------------------------------------------- small dancer bands
dosmall                         ; band B first: it is drawn ahead of the
        lda #100                ; beam, band A after the beam has passed
        jsr waitline
        lda #0
        sta rowi
-       ldx lsph                ; band B, rows 15-22, moving right
        lda ph8,x
        clc
        adc rowi
        tax
        lda smallrowlo,x
        clc
        adc #40
        sta srcp
        lda smallrowhi,x
        adc #0
        sta srcp+1
        lda srcp
        clc
        adc lposb
        sta srcp
        lda srcp+1
        adc #0
        sta srcp+1
        lda rowi
        clc
        adc #14
        tax
        jsr callrow
        inc rowi
        lda rowi
        cmp #8
        bne -
        lda #0
        sta rowi
-       ldx lsph                ; band A, rows 1-8, moving left
        lda ph8,x
        clc
        adc rowi
        tax
        lda smallrowlo,x
        clc
        adc lposa
        sta srcp
        lda smallrowhi,x
        adc #0
        sta srcp+1
        ldx rowi
        jsr callrow
        inc rowi
        lda rowi
        cmp #8
        bne -
        jmp done

; ------------------------------------------------- band colours
docolours
        ldx #1
-       lda smcol-1,x
        jsr setrowcol
        inx
        cpx #9
        bne -
        ldx #15
-       lda smcol-15,x
        jsr setrowcol
        inx
        cpx #23
        bne -
        jmp done

; ------------------------------------------------- dungeon strip on
dodclear
        lda #200
        jsr waitline
        ldx #239                ; rows 9-14 to the dungeon blank
        lda #0
-       sta SCREEN+9*40,x
        dex
        cpx #$ff
        bne -
        lda #<ADDR_DNG
        sta dptr
        lda #>ADDR_DNG
        sta dptr+1
        lda #1
        sta dng
        jmp done

; colour row X with A (keeps X)
setrowcol
        pha
        lda rowlo,x
        sta dstp
        lda rowhi,x
        clc
        adc #>(COLRAM-SCREEN)
        sta dstp+1
        pla
        ldy #39
-       sta (dstp),y
        dey
        bpl -
        rts

; ------------------------------------------------------------ IRQ A
irqa
        pha
        txa
        pha
        tya
        pha
        lda o                   ; next fine scroll step
        clc
        adc #1
        and #7
        sta o
        sta xstop               ; top row left to right: o
        sta $d016
        eor #7                  ; right to left: 7-o
        sta xsbot
        sta xsmid
        lda mode
        cmp #2
        bcc +
        lda #0                  ; portrait has stopped: middle stays put
        sta xsmid
+       lda o
        bne +
        jsr shifttext
+       lda dng
        beq +
        lda o
        cmp #4
        bne +
        jsr dstep
+       jsr logic
        lda #<irqb
        sta $fffe
        lda #>irqb
        sta $ffff
        lda #56
        sta $d012
        lda #$ff
        sta $d019
        pla
        tay
        pla
        tax
        pla
nmi     rti

; move both text rows one character and feed the next letters
shifttext
        ldx #38                 ; top row moves right
-       lda SCREEN,x
        sta SCREEN+1,x
        dex
        bpl -
        ldy #0
        lda (topp),y
        cmp #$ff
        bne +
        lda #<ADDR_TOP
        sta topp
        lda #>ADDR_TOP
        sta topp+1
        lda (topp),y
+       sta SCREEN
        inc topp
        bne +
        inc topp+1
+       ldx #0                  ; bottom row moves left
-       lda SCREEN+24*40+1,x
        sta SCREEN+24*40,x
        inx
        cpx #39
        bne -
        lda (botp),y
        cmp #$ff
        bne +
        lda #<ADDR_BOT
        sta botp
        lda #>ADDR_BOT
        sta botp+1
        lda (botp),y
+       sta SCREEN+24*40+39
        inc botp
        bne +
        inc botp+1
+       rts

; what happens this frame
logic
        lda mode
        cmp #2
        bcs notbig
        lda o                   ; dancers / portrait coming in
        cmp #7                  ; ask for the next column on the last step
        bne lret
        lda req
        bne lret
        lda mode
        beq +
        lda tstep               ; portrait is centred: stop here
        cmp #40
        bne +
        lda #2
        sta mode
        lda #1
        sta wrow
        rts
+       inc pos
        lda pos
        cmp #40+BIG_LINE
        bne +
        lda #40
        sta pos
+       inc wraps
        lda wraps
        and #1
        bne +
        lda ph
        clc
        adc #1
        and #3
        sta ph
+       lda mode
        bne inoutro
        lda fcnt+1              ; has the song ended?
        cmp songend+1
        bcc issue
        bne +
        lda fcnt
        cmp songend
        bcc issue
+       lda #1
        sta mode
inoutro
        inc tstep
issue
        lda pos
        sta lpos
        lda ph
        sta lph
        lda tstep
        sta lt
        lda #1
        sta req
lret    rts

notbig
        cmp #2
        bne notwipe
        ldx wrow                ; colour wipe to white, a row a frame
        lda rowlo,x
        sta idstp
        lda rowhi,x
        clc
        adc #>(COLRAM-SCREEN)
        sta idstp+1
        lda #1
        ldy #39
-       sta (idstp),y
        dey
        bpl -
        inc wrow
        lda wrow
        cmp #23
        bne +
        lda #3
        sta mode
        lda #50
        sta timer
        lda #<ADDR_FRAMES
        sta recp
        lda #>ADDR_FRAMES
        sta recp+1
+       rts

notwipe
        cmp #3
        bne notshrink
        dec timer               ; shrink a step every 4 frames
        bne +
        lda #4
        sta timer
        lda req
        bne +
        ldy #0
        lda (recp),y
        bne ++
        lda #4                  ; all steps done
        sta mode
        lda #50
        sta timer
        rts
++      lda #2
        sta req
+       rts

notshrink
        cmp #4
        bne notpause
        dec timer
        bne +
        lda #4
        sta req
        lda #5
        sta mode
        lda #0
        sta posa
        sta sph
        sta sstep
        lda #40+SM_LINE
        sta posb
        lda #1                  ; portrait shrinks away as the bands come in
        sta timer
        lda #<ADDR_FRAMES2
        sta recp
        lda #>ADDR_FRAMES2
        sta recp+1
+       rts

notpause
        lda fcnt                ; small bands step on even frames
        and #1
        beq ++
        lda dng                 ; odd frames: shrink, then the dungeon
        bne +
        dec timer
        bne +
        lda #4
        sta timer
        lda req
        bne +
        ldy #0
        lda (recp),y
        bne shr
        lda #5                  ; portrait gone: dungeon strip on
        sta req
        lda #$ff
        sta timer
        rts
shr     lda #2
        sta req
+       rts
++      lda req
        bne +
        inc posa
        lda posa
        cmp #40+SM_LINE
        bne ++
        lda #40
        sta posa
++      dec posb
        lda posb
        cmp #$ff
        bne ++
        lda #SM_LINE-1
        sta posb
++      inc sstep
        lda sstep
        and #7
        bne ++
        lda sph
        clc
        adc #1
        and #3
        sta sph
++      lda posa
        sta lposa
        lda posb
        sta lposb
        lda sph
        sta lsph
        lda #3
        sta req
+       rts

; ------------------------------------------------------------ IRQ B
irqb
        pha
        txa
        pha
        tya
        pha
-       lda $d012               ; last line of row 0
        cmp #58
        bcc -
        ldx #8                  ; to the end of that line
-       dex
        bne -
        nop
        nop
        lda xsmid
        sta $d016
        jsr MUSIC_PLAY
        inc fcnt
        bne +
        inc fcnt+1
+       lda dng
        beq +
        lda #<irqd
        sta $fffe
        lda #>irqd
        sta $ffff
        lda #120
        bne ++
+       lda #<irqc
        sta $fffe
        lda #>irqc
        sta $ffff
        lda #238
++      sta $d012
        lda #$ff
        sta $d019
        pla
        tay
        pla
        tax
        pla
        rti

; ------------------------------------------------------------ IRQ D / E
irqd
        pha
        txa
        pha
-       lda $d012               ; end of the last line of row 8
        cmp #122
        bcc -
        ldx #8
-       dex
        bne -
        nop
        nop
        nop                     ; write lands at the end of the line
        nop
        lda #$12                ; screen $0400, dungeon font $0800
        sta $d018
        lda #<irqe
        sta $fffe
        lda #>irqe
        sta $ffff
        lda #168
        sta $d012
        lda #$ff
        sta $d019
        pla
        tax
        pla
        rti

irqe
        pha
        txa
        pha
-       lda $d012               ; end of the last line of row 14
        cmp #170
        bcc -
        ldx #8
-       dex
        bne -
        nop
        nop
        nop                     ; write lands at the end of the line
        nop
        lda #$14                ; ROM font again
        sta $d018
        lda #<irqc
        sta $fffe
        lda #>irqc
        sta $ffff
        lda #238
        sta $d012
        lda #$ff
        sta $d019
        pla
        tax
        pla
        rti

; one dungeon step: count, then count x (offset in rows 9-14, glyph)
dstep
        ldy #0
        lda (dptr),y
        cmp #$ff
        bne +
        lda #<ADDR_DNG          ; back to the first level
        sta dptr
        lda #>ADDR_DNG
        sta dptr+1
        lda (dptr),y
+       tax
        inc dptr
        bne +
        inc dptr+1
+       cpx #0
        beq dsdone
dsloop  ldy #1
        lda (dptr),y            ; glyph
        sta dgl
        dey
        lda (dptr),y            ; offset
        tay
        lda dgl
        sta SCREEN+9*40,y
        stx dcnt
        tax
        lda ADDR_DCOL,x
        sta COLRAM+9*40,y
        ldx dcnt
        lda dptr
        clc
        adc #2
        sta dptr
        bcc +
        inc dptr+1
+       dex
        bne dsloop
dsdone  rts

; ------------------------------------------------------------ IRQ C
irqc
        pha
        lda xsbot
        sta $d016
        lda #<irqa
        sta $fffe
        lda #>irqa
        sta $ffff
        lda #10
        sta $d012
        lda #$ff
        sta $d019
        pla
        rti

; ------------------------------------------------------------ tables
bigcol  !byte 1,1,1,1,1,1, 15,15,15,15,15, 12,12,12,12,12, 11,11,11,11,11,11
smcol   !byte 1,1,15,15,12,12,11,11
ph23    !byte 0,23,46,69
ph8     !byte 0,8,16,24
rowlo   !for r, 0, 24 { !byte <(SCREEN + r*40) }
rowhi   !for r, 0, 24 { !byte >(SCREEN + r*40) }
mul7lo  !for c, 0, 40 { !byte <(c*7) }
mul7hi  !for c, 0, 40 { !byte >(c*7) }
; 23 rows: screen rows 1-22, then the colour row for the labels (row 21)
rowcodelo !for r, 0, 22 { !byte <(ROWCODE + r*ROWSIZE) }
rowcodehi !for r, 0, 22 { !byte >(ROWCODE + r*ROWSIZE) }
outrolo !for r, 0, 21 { !byte <(ADDR_OUTRO + r*40) }
        !byte <ADDR_OUTROCOL
outrohi !for r, 0, 21 { !byte >(ADDR_OUTRO + r*40) }
        !byte >ADDR_OUTROCOL
bigrowlo !for p, 0, 3 { !for r, 0, 21 { !byte <(ADDR_BIG + p*BIG_PHASE + r*BIG_W) } : !byte <ADDR_COLSTRIP }
bigrowhi !for p, 0, 3 { !for r, 0, 21 { !byte >(ADDR_BIG + p*BIG_PHASE + r*BIG_W) } : !byte >ADDR_COLSTRIP }
smallrowlo !for p, 0, 3 { !for r, 0, 7 { !byte <(ADDR_SMALL + p*SM_PHASE + r*SM_W) } }
smallrowhi !for p, 0, 3 { !for r, 0, 7 { !byte >(ADDR_SMALL + p*SM_PHASE + r*SM_W) } }

; unrolled row drawing: screen row r+1, columns 0-39 from (srcp),y
ROWCODE
!for r, 0, 21 {
        !for c, 0, 39 {
                ldy #c
                lda (srcp),y
                sta SCREEN + (r+1)*40 + c
        }
        rts
}
        !for c, 0, 39 {         ; row 22 of the code: label colours, row 21
                ldy #c
                lda (srcp),y
                sta COLRAM + 21*40 + c
        }
        rts
CODE_END

!if CODE_END > ADDR_BIG { !error "code runs into the dancer strips" }

; dancer strips and texts go in the same file
* = ADDR_BIG
!binary "build/big.bin"
* = ADDR_TEXT
!binary "build/texts.bin"
