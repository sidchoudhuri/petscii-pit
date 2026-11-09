; PETSCII Pit: SID model check (test build). Placed by the loader at $0720.
; Three readings of voice 3 for the chip at $D400 (off=0) or $D420 (off=$20):
;  A: classic check - oscillator reset with the test bit at frequency $FFFF,
;     sawtooth started, oscillator read 4 cycles later (models differ by one
;     step in the value read back)
;  B: how many of 256 readings are not zero with sawtooth+triangle combined
;  C: the same with pulse+sawtooth combined (pulse width 50%)
        * = $0720
off     !byte 0         ; 1824: 0 = chip at $D400, $20 = chip at $D420
ra      !byte 0         ; 1825: result A
rb      !byte 0         ; 1826: result B
rc      !byte 0         ; 1827: result C
; SYS 1828
        sei
        ldx off
        lda #$ff
        sta $d412,x     ; test bit (and every waveform) on voice 3
        sta $d40e,x     ; frequency $FFFF
        sta $d40f,x
        lda #$20
        sta $d412,x     ; sawtooth, test bit off: the oscillator starts
        lda $d41b,x     ; read it straight away
        sta ra
        lda #0          ; B: sawtooth+triangle, frequency $4000
        sta $d40e,x
        lda #$40
        sta $d40f,x
        lda #$30
        jsr count
        sta rb
        lda #0          ; C: pulse+sawtooth, pulse width 50%
        sta $d410,x
        lda #$08
        sta $d411,x
        lda #$50
        jsr count
        sta rc
        lda #0
        sta $d412,x
        sta $d40e,x
        sta $d40f,x
        sta $d410,x
        sta $d411,x
        cli
        rts
count   pha
        lda #$08        ; test bit: reset the oscillator
        sta $d412,x
        pla
        sta $d412,x     ; waveform, gate off
        ldy #0
        sty tmp
-       lda $d41b,x
        beq +
        inc tmp
+       dey
        bne -
        lda #$08
        sta $d412,x
        lda tmp
        rts
tmp     !byte 0
