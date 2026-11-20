; PETSCII Pit STORY: level reading and unpacking, at $9400 (top of BASIC is
; lowered to $934C by the STORY game; $934C-$93FF the bleed routine,
; bleed.asm; $94F6-$94FD the name "LEVELIDX"; the level index LEVELIDX is
; kept at $BC00-$BD31, under the BASIC ROM, and
; copied to $C400 just before each level is read). The level is read into the fog map at $C400 (up to 4
; blocks, ending at $C7F7), which the game clears again after unpacking.
; Installed by the loader just before it loads STORY.
; Zero page $57-$5A during a SYS only (the music IRQ uses $FB/$FC).
;
; SYS 37888 READ BLOCK: logical file 2 is open on the drive's buffer and a
;   U1 command has read a block into it. Reads the 256 bytes: the link
;   (next track, sector) goes to lnkt/lnks, the 254 data bytes go to the
;   buffer at bp, and bp moves on by 254. BASIC sets bp to $C400 first.
; SYS 37891 UNPACK: finds MA% and unpacks the map runs starting at src into
;   MA%(120)-MA%(999) (high byte 0, low byte = cell type).

        * = $9400
        jmp rdblk
        jmp unpack
bp      !word $c400     ; 37894/37895: where the next block goes
lnkt    !byte 0         ; 37896: next track
lnks    !byte 0         ; 37897: next sector
src     !word 0         ; 37898/37899: first map byte (set by BASIC)
cnt     !byte 0
run     !byte 0
typ     !byte 0
cells   !word 0

rdblk   ldx #2
        jsr $ffc6       ; CHKIN
        jsr $ffcf       ; CHRIN
        sta lnkt
        jsr $ffcf
        sta lnks
        lda bp
        sta $57
        lda bp+1
        sta $58
        lda #254
        sta cnt
-       jsr $ffcf
        ldy #0
        sta ($57),y
        inc $57
        bne +
        inc $58
+       dec cnt
        bne -
        lda $57
        sta bp
        lda $58
        sta bp+1
        jmp $ffcc       ; CLRCHN

; find the integer array MA% ("M"+$80, "A"+$80) between ($2F) and ($31)
unpack  lda $2f
        sta $57
        lda $30
        sta $58
find    lda $58
        cmp $32
        bcc +
        bne nofind
        lda $57
        cmp $31
        bcs nofind
+       ldy #0
        lda ($57),y
        cmp #$cd
        bne next
        iny
        lda ($57),y
        cmp #$c1
        beq found
next    ldy #2
        lda ($57),y
        clc
        adc $57
        tax
        iny
        lda ($57),y
        adc $58
        sta $58
        stx $57
        jmp find
nofind  rts
; data 7 bytes in; skip to cell 120 (240 bytes)
found   lda $57
        clc
        adc #7+240
        sta $57
        bcc +
        inc $58
+       lda src
        sta $59
        lda src+1
        sta $5a
        lda #<880
        sta cells
        lda #>880
        sta cells+1
rbyte   ldy #0
        lda ($59),y
        inc $59
        bne +
        inc $5a
+       tax
        and #15
        sta run
        inc run         ; run length 1-16
        txa
        lsr
        lsr
        lsr
        lsr
        sta typ
-       ldy #0
        tya
        sta ($57),y     ; high byte
        iny
        lda typ
        sta ($57),y     ; low byte
        lda $57
        clc
        adc #2
        sta $57
        bcc +
        inc $58
+       lda cells
        bne +
        dec cells+1
+       dec cells
        lda cells
        ora cells+1
        beq done
        dec run
        bne -
        jmp rbyte
done    rts
end
