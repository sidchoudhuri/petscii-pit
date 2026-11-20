; PETSCII Pit STORY (V29): the world turns back into PETSCII.
; At $934C (37708), just below the story routine at $9400; STORY's top of
; BASIC is $934C. Installed by the loader with story.asm, just before STORY
; loads.
;
; POKE 37708,level : SYS 37709
;   Puts the whole character set back from the copy the loader keeps at
;   $F000-$F7FF (under the KERNAL), then, for every group whose level has
;   been reached, copies those glyphs from the character ROM over the
;   custom ones at $C800. Level 0-59 leaves every custom glyph in place.
; Zero page $57-$5A during the SYS only.

        * = $934c
lvl     !byte 0
bleed   sei
        lda #$35        ; RAM at $F000, I/O in
        sta $01
        lda #0
        sta $57
        sta $59
        lda #$f0
        sta $58
        lda #$c8
        sta $5a
        ldx #8
        ldy #0
-       lda ($57),y
        sta ($59),y
        iny
        bne -
        inc $58
        inc $5a
        dex
        bne -
        lda #$33        ; character ROM at $D000
        sta $01
        ldx #0
grp     lda tab,x       ; the level a group reverts at (0 = end)
        beq done
        lda lvl
        cmp tab,x
        bcc done        ; not that deep yet
        inx
        lda tab,x       ; how many glyphs
        sta $5b
        inx
-       lda tab,x
        jsr rom
        inx
        dec $5b
        bne -
        beq grp
done    lda #$37
        sta $01
        cli
        rts

; copy glyph A from the character ROM ($D000) to the font ($C800)
rom     sta $57
        lda #0
        sta $58
        asl $57
        rol $58
        asl $57
        rol $58
        asl $57
        rol $58
        lda $57
        sta $59
        lda $58
        clc
        adc #$c8
        sta $5a
        lda $58
        clc
        adc #$d0
        sta $58
        ldy #7
-       lda ($57),y
        sta ($59),y
        dey
        bpl -
        rts

; level, count, screen codes: decorations, then the floor, monsters, CHAR,
; and the player last
tab     !byte 60, 2, 132, 158                         ; chests, potions
        !byte 65, 9, 166, 167, 190, 104, 105, 106, 107, 108, 109 ; runes, notes, stairs, weapons
        !byte 70, 1, 159                              ; floor
        !byte 80, 6, 83, 211, 88, 216, 90, 218        ; leech, goblin, imp
        !byte 85, 8, 86, 214, 91, 219, 84, 212, 65, 193 ; guard, cultist, serpent, golem
        !byte 90, 2, 85, 213                          ; CHAR's counter
        !byte 95, 2, 89, 217                          ; CHAR
        !byte 100, 4, 128, 129, 130, 144              ; the player
        !byte 0
end
