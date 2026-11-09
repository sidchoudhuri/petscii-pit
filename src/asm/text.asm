; PETSCII Pit: game text kept in the RAM under the BASIC ROM.
; The loader writes the messages to $B200 (45568) as a list: a length byte,
; then the PETSCII bytes. Messages are numbered from 1.
; This code sits at $0400 (the old screen, unused since the screen moved to
; $C000); the buffer is at $0480. Installed by the loader.
; Zero page $57-$5A during a SYS only (the music IRQ uses $FB/$FC; the music
; player uses the cassette buffer and $02A7, so they are not used here).
;
; SYS 1024,N  PRINT message N at the cursor (same as PRINT "...";)
; SYS 1027,N  FETCH message N into the buffer (length at 1152, text after it)
; SYS 1030    PUT: copy the buffer text into the newest string, which BASIC
;             has just made the right length with MS$=LEFT$(BL$,PEEK(1152))

bank    = $b200
buf     = $0480

        * = $0400
        jmp prt
        jmp fet
put     ldy buf
        beq +
-       lda buf,y       ; text byte y (1..len) goes to string byte y-1
        dey
        sta ($33),y     ; $33/$34: bottom of string space = newest string
        bne -
+       rts

prt     lda #1
        !byte $2c       ; skip the next two bytes
fet     lda #0
        sta $5a
        jsr $aefd       ; CHKCOM
        jsr $b79e       ; GETBYT: message number to X
        lda #<bank
        sta $57
        lda #>bank
        sta $58
        lda $01
        sta $59
        and #$fe        ; BASIC ROM out, KERNAL and I/O stay in
        sta $01
        ldy #0
walk    dex
        beq found
        lda ($57),y     ; skip this message: length + 1
        sec
        adc $57
        sta $57
        bcc walk
        inc $58
        bcs walk
found   lda ($57),y
        sta buf
        tax
        beq done
-       iny
        lda ($57),y
        sta buf,y
        dex
        bne -
done    lda $59
        sta $01
        lda $5a
        beq out
        ldy #0
-       cpy buf
        beq out
        lda buf+1,y
        jsr $ffd2       ; CHROUT keeps X and Y
        iny
        bne -
out     rts
