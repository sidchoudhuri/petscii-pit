; PETSCII Pit ENDING (V29): the character ROM, seen in a mirror.
; At 828 (the cassette buffer). SYS 828 copies the upper case set from the
; character ROM ($D000-$D7FF) to $3000-$37FF with every byte's bits reversed,
; so each letter faces the other way.

        * = 828
        sei
        lda #$33
        sta $01
        lda #0
        sta $fb
        sta $fd
        lda #$d0
        sta $fc
        lda #$30
        sta $fe
        ldx #8
page    ldy #0
byte    lda ($fb),y
        sta $02
        lda #1          ; marker bit: out into carry after eight turns
-       lsr $02
        rol
        bcc -
        sta ($fd),y
        iny
        bne byte
        inc $fc
        inc $fe
        dex
        bne page
        lda #$37
        sta $01
        cli
        rts
