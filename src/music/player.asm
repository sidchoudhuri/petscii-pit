; ---------------------------------------------------------------------------
; PETSCII Pit music player - 2 songs: 0 "Dungeoneering", 1 "Fight"
; Original compositions. Player techniques: hard-restart gating, table-driven
; waveform/note programs (drums, octave/diminished arps), bouncing pulse-width
; sweep, delayed triangle vibrato. Pattern-based data: per-voice order lists
; of (pattern, transpose).
;
; Build:  python3 build.py   (generates music.asm, assembles, wraps PSID)
; Lives at BASE-$9FFF, just under BASIC ROM. Programs using it lower the
; top of BASIC first: POKE 55,0:POKE 56,BASE/256:CLR
; Uses zero page $FB/$FC in the player; $FD/$FE and $22/$23 in the helpers.
;
; Entry points (offset from BASE):
;   +0  init   - A = song (PSID init)
;   +3  play   - one frame (PSID play)
;   +6  start  - Dungeoneering from the top, played on a 50 Hz raster IRQ
;   +9  stop   - remove the IRQ, silence the SID
;   +12 fx     - hand voice 1 to the game's sound effects
;   +15 fxhold byte: POKE BASE+15,0 hands voice 1 back to the music
;   +16 clrarr - see below
;   +19 clrmap - see below
;   +22 fight  - switch to the fight song (Dungeoneering position is saved)
;   +25 resume - back to Dungeoneering where it left off
;   +28 pause  - silence the music, keeping its place
;   +31 unpause- carry on from where pause stopped (voices re-enter on their next note)
;   +34 mood   - A = 0 happy (Dungeoneering) / 1 sad (Lamenting); each keeps its place
;   +37 sids   byte: 2 = second SID at $D420 (music stays on $D400, the game
;              writes its effects to $D420), 1 = one SID (PEEK it);
;              POKE 0 (detect at the next start), 1 or 2 (forced) before start
;   38653      start mood: POKE 1 before start to begin with Lamenting
; ---------------------------------------------------------------------------

SID     = $d400
; In-game mix options (build.py sets them; stand-alone .sid files leave them out):
;   HRSR   - SR value written at hard restart (1 = gentle release, no click)
;   CUTOFF - route the music through the low-pass filter at this cutoff
!ifndef HRSR { HRSR = 0 }
ZP      = $fb               ; $fb/$fc data pointer
mchip   = BASE - 5          ; 38651: 1 = music on $D420 (two SIDs only)
smood   = BASE - 3          ; 38653: mood start begins with (0 happy, 1 sad)

        * = BASE - $100

; ---------------------------------------------------------------------------
; Look for a second SID at $D420 (once). On a stock C64 the SID repeats every
; 32 bytes, so $D420 is SID 1 again. Voice 3's oscillator readout ($D41B /
; $D43B) tells them apart: the test bit ($08) holds an oscillator at 0.
detect
        lda sids
        bne setsid          ; set by the loader (S): 1 or 2, use it as it is
        lda #1
        sta sids            ; assume one SID
        lda #$ff
        sta $d40e           ; SID 1 voice 3: fast sawtooth
        sta $d40f
        sta $d42e           ; same for voice 3 at $D420
        sta $d42f
        lda #$20
        sta $d412
        lda #$28
        sta $d432           ; test bit at $D420: stops SID 1 if it is a mirror
        lda $d41b
        ora $d41b
        ora $d41b
        ora $d41b
        beq detend          ; SID 1 stopped: $D420 is a mirror, one SID
        lda #$20
        sta $d432           ; run voice 3 on the second chip
        lda $d43b
        ora $d43b
        ora $d43b
        ora $d43b
        beq detend          ; nothing moving at $D420: one SID
        lda #$28
        sta $d432
        lda $d43b
        bne detend          ; test bit didn't stop it: not a real second SID
        lda #2
        sta sids            ; second SID found: the effects move to it
detend  lda #0
        sta $d412
        sta $d432
; sids 1: music and effects on $D400. sids 2: music on $D400 and effects
; on $D420, or the other way round when mchip (38651) is 1
setsid  ldx #0              ; effects chip offset
        ldy #0              ; music chip offset
        lda sids
        cmp #2
        bne +
        ldx #$20
        lda mchip
        beq +
        ldx #0
        ldy #$20
+       stx fxoff
        sty moff
        sty tmps
        ldx #2
-       lda sidoff,x
        and #$1f
        ora tmps
        sta sidoff,x
        dex
        bpl -
        rts
fxoff   !byte 0             ; 0 = effects on $D400, $20 = effects on $D420
moff    !byte 0             ; 0 = music on $D400, $20 = music on $D420

; set both chips' volume from the saved settings (38641 music, 38642
; effects, each stored +1; 0 = not set yet: the loader's defaults, 3 and 15
; with two SIDs, 9 with one), so the music never starts at full volume
setvol  lda BASE-14         ; effects volume + 1
        bne +
        lda #16
        ldx sids
        cpx #2
        beq +
        lda #10
+       sec
        sbc #1
        ldx fxoff
        sta $d418,x
        lda BASE-15         ; music volume + 1
        bne +
        lda #4
        ldx sids
        cpx #2
        beq +
        lda #10
+       sec
        sbc #1
        ldx moff
        sta $d418,x         ; last, so with one SID the music volume wins
        rts

        !fill BASE - *, 0
        * = BASE

        jmp init
        jmp play
        jmp start
        jmp stop
        jmp fxbegin
fxhold  !byte 0             ; non-zero while a game sound effect owns voice 1
        jmp clrarr
        jmp clrmap
        jmp fight
        jmp resume
        jmp pause
        jmp unpause
        jmp setmood
sids    !byte 0             ; 0 = not checked yet, 1 = one SID, 2 = second SID at $D420

; ---------------------------------------------------------------------------
; PETSCII Pit helpers (level generation speed-ups)
;
; BASE+16 clrarr - zero the data of the first A arrays in BASIC's array
;                        area (headers untouched). POKE 780,n:SYS BASE+16
; BASE+19 clrmap - zero 1000 bytes starting at X/Y (lo/hi).
;                        POKE 781,lo:POKE 782,hi:SYS BASE+19
; Uses zero page $FD/$FE and $22/$23 (BASIC temporaries), never $FB/$FC,
; so the music IRQ can keep running.
AP      = $fd               ; current array
DP      = $22               ; current data byte

clrarr
        tax
        beq clrdone
        lda $2f             ; start of arrays
        sta AP
        lda $30
        sta AP+1
nextarr
        ldy #2              ; total array length incl. header
        lda (AP),y
        sta alen
        iny
        lda (AP),y
        sta alen+1
        ldy #4              ; header = 5 + 2 * dimensions
        lda (AP),y
        asl
        clc
        adc #5
        sta ahdr
        clc
        lda AP
        adc ahdr
        sta DP
        lda AP+1
        adc #0
        sta DP+1
        sec
        lda alen
        sbc ahdr
        sta zlen
        lda alen+1
        sbc #0
        sta zlen+1
        jsr zerofill
        clc                 ; next array
        lda AP
        adc alen
        sta AP
        lda AP+1
        adc alen+1
        sta AP+1
        dex
        bne nextarr
clrdone rts

clrmap
        stx DP
        sty DP+1
        lda #<1000
        sta zlen
        lda #>1000
        sta zlen+1
        ; fall through

; zero zlen bytes at (DP)
zerofill
        lda #0
-       ldy zlen+1
        beq ztail
        ldy #0
--      sta (DP),y
        iny
        bne --
        inc DP+1
        dec zlen+1
        jmp -
ztail   ldy zlen
        beq zdone
-       dey
        sta (DP),y
        bne -
zdone   rts

alen    !word 0
ahdr    !byte 0
zlen    !word 0

; ---------------------------------------------------------------------------
; start music on a raster IRQ. The KERNAL's 60 Hz CIA IRQ keeps running
; untouched (TI, keyboard), raster IRQs only play the tune and return.
start
        sei
        jsr detect
        lda #0
        sta paused
        sta usedd           ; start always begins happy, at the top
        sta usedl
        lda smood           ; start mood: 0 Dungeoneering, 1 Lamenting (POKE 38653)
        and #1
        sta mood
        asl                 ; song 0 or 2
        jsr init
        lda #0
        sta fxhold
        sta blocked
        lda #<irq
        sta $0314
        lda #>irq
        sta $0315
        lda #$f8
        sta $d012
        lda $d011
        and #$7f
        sta $d011
        lda #1
        sta $d019
        sta $d01a
        cli
        rts

stop
        sei
        lda #0
        sta $d01a
        lda #1
        sta $d019
        lda #$31
        sta $0314
        lda #$ea
        sta $0315
        cli
        jsr silence         ; music voices off
        ldy fxoff
        lda #0
        sta SID+4,y         ; effects voice off
        lda #$09            ; voice 1 envelope the game's effects expect
        sta SID+5,y
        lda #$00
        sta SID+6,y
!ifdef CUTOFF {
        lda #0
        sta SID+$17         ; nothing through the filter
}
        jmp setvol

irq
        lda $d019
        and #1
        beq +
        sta $d019           ; acknowledge raster IRQ
        jsr play
        jmp $ea81           ; restore registers, RTI
+       jmp $ea31           ; CIA IRQ: normal KERNAL handler

; game sound effect takes voice 1: silence it, set the effects' envelope
fxbegin
        ldy fxoff
        lda sids
        cmp #2
        beq +               ; effects on their own chip: nothing to hand over
        lda #1
        sta fxhold
        sta blocked
!ifdef CUTOFF {
        lda #$06            ; the effect's voice skips the filter
        sta SID+$17
}
+       lda #0
        sta SID+4,y
        lda #$09
        sta SID+5,y
        lda #$00
        sta SID+6,y
        rts

; ---------------------------------------------------------------------------
init
        jsr setsong
        ldx #$38
        lda #0
-       sta SID,x           ; clear all SID registers (both chips)
        dex
        bpl -
!ifdef CUTOFF {
        lda #CUTOFF
        sta SID+$16
        lda #$07            ; all three voices through the filter
        sta SID+$17
        lda #$1f            ; low-pass, volume max
        sta SID+$18
}
        jmp setvol          ; volume from the saved settings, not full

; set up all three voices for song A
setsong
        sta cursong
        sta tmps
        asl
        clc
        adc tmps
        tay                 ; Y = song * 3
        ldx #0
-       lda songlo,y
        sta olo,x
        lda songhi,y
        sta ohi,x
        lda #0
        sta opos,x
        sta hr,x
        sta ctrl,x
        sta blocked,x
        lda #1
        sta cnt,x           ; fetch first event on first play call
        sta resting,x
        tya
        pha
        jsr nextpat
        pla
        tay
        iny
        inx
        cpx #3
        bne -
        rts

; next order list entry for voice X: pattern pointer and transpose
nextpat
        lda olo,x
        sta ZP
        lda ohi,x
        sta ZP+1
        ldy opos,x
        lda (ZP),y
        cmp #$ff
        bne +
        iny                 ; end: jump to the loop entry
        lda (ZP),y
        tay
        lda (ZP),y
+       sta tmpp
        iny
        lda (ZP),y
        sta trn,x
        iny
        tya
        sta opos,x
        ldy tmpp
        lda patlo,y
        sta ptrlo,x
        lda pathi,y
        sta ptrhi,x
        rts

; ---------------------------------------------------------------------------
; song switching. fight saves the whole Dungeoneering voice state, resume
; puts it back. Voices stay muted after a switch-back until their next
; event, so nothing half-finished is heard.
fight
        lda #0
        sta paused
        lda cursong
        cmp #1
        beq swdone
        sei
        jsr saveamb
        lda #1
        jsr setsong
        jsr silence
        cli
swdone  rts

pause
        lda #1
        sta paused
        jmp silence

unpause
        lda paused
        beq +
        lda #0
        sta paused
        lda #1
        sta blocked
        sta blocked+1
        sta blocked+2
+       rts

resume
        lda cursong
        cmp #1
        bne swdone
        sei
        jsr loadamb
        jsr mute
        cli
        rts

; set the mood: A = 0 happy (Dungeoneering), 1 sad (Lamenting). During a
; fight it is only remembered; resume then returns to that mood's song.
setmood
        and #1
        cmp mood
        beq swdone
        sei
        sta newmd
        lda cursong
        cmp #1
        beq +
        jsr saveamb
        lda newmd
        sta mood
        jsr loadamb
        jsr mute
        cli
        rts
+       lda newmd
        sta mood
        cli
        rts

; save the playing mood song (song 0 or 2) so it can carry on later
saveamb
        ldx #VSLEN-1
        lda cursong
        bne ++
-       lda vstate,x
        sta vsave,x
        dex
        bpl -
        lda #1
        sta usedd
        rts
++
-       lda vstate,x
        sta lsave,x
        dex
        bpl -
        lda #1
        sta usedl
        rts

; bring back the current mood's song where it left off (or from the top)
loadamb
        ldx #VSLEN-1
        lda mood
        bne ++
        lda usedd
        beq +
-       lda vsave,x
        sta vstate,x
        dex
        bpl -
        lda #0
        sta cursong
        rts
+       lda #0
        jmp setsong
++      lda usedl
        beq +
-       lda lsave,x
        sta vstate,x
        dex
        bpl -
        lda #2
        sta cursong
        rts
+       lda #2
        jmp setsong

; voices stay silent until their next note
mute
        lda #1
        sta blocked
        sta blocked+1
        sta blocked+2
        jmp silence

; gate off, envelope 0 on every voice the music owns
silence
        ldx #2
-       cpx #0
        bne +
        lda fxhold          ; voice 1 belongs to an effect right now
        bne ++
+       ldy sidoff,x
        lda #0
        sta SID+4,y
        sta SID+5,y
        sta SID+6,y
++      dex
        bpl -
        rts

; ---------------------------------------------------------------------------
play
        lda paused
        beq +
        rts
+
!ifdef CUTOFF {
        lda #$07            ; music voices through the filter,
        ldy fxhold          ; but never a sound effect
        beq +
        lda #$06
+       sta SID+$17
}
        lda fxhold          ; while an effect plays, voice 1 stays muted
        beq +               ; until its next event after the effect ends
        sta blocked
+       ldx #0
-       jsr voice
        inx
        cpx #3
        bne -
        rts

; ---------------------------------------------------------------------------
; per-voice tick, X = voice 0..2
voice
        dec cnt,x
        lda cnt,x
        cmp #2
        bne +
        ; two frames before the next event: hard restart (gate off, ADSR 0)
        lda resting,x
        ora blocked,x
        bne +
        ldy sidoff,x
        lda ctrl,x
        and #$fe
        sta SID+4,y
        lda #0
        sta SID+5,y
!if HRSR {
        lda #HRSR           ; gentle release instead of an instant cut
}
        sta SID+6,y
        lda #1
        sta hr,x
+       lda cnt,x
        bne +
        jsr fetch
+       lda resting,x
        ora hr,x
        bne +
        jmp update
+       rts

; ---------------------------------------------------------------------------
; read next 3-byte event: instrument, note (0 = rest), duration in frames
; $ff = end of pattern, continue with the next order list entry
fetch
        lda ptrlo,x
        sta ZP
        lda ptrhi,x
        sta ZP+1
        ldy #0
        lda (ZP),y
        cmp #$ff
        bne +
        jsr nextpat         ; end of pattern
        lda ptrlo,x
        sta ZP
        lda ptrhi,x
        sta ZP+1
        ldy #0
        lda (ZP),y
+       sta inst,x
        iny
        lda (ZP),y
        beq +               ; rest: not transposed
        clc
        adc trn,x
+       sta note,x
        iny
        lda (ZP),y
        sta cnt,x
        clc
        lda ZP
        adc #3
        sta ptrlo,x
        lda ZP+1
        adc #0
        sta ptrhi,x

        lda #0
        sta hr,x
        lda fxhold          ; effect finished: voice may sound again
        bne +
        sta blocked,x
+       lda note,x
        bne startnote
        ; rest: release the gate and stay silent
        lda #1
        sta resting,x
        lda ctrl,x
        and #$fe
        sta ctrl,x
        ldy blocked,x
        bne +
        ldy sidoff,x
        sta SID+4,y
+       rts

startnote
        lda #0
        sta resting,x
        sta vdir,x
        sta voffl,x
        sta voffh,x
        ldy inst,x
        lda i_wt,y
        sta wtpos,x
        lda i_pw,y
        sta pwhi,x
        lda #0
        sta pwlo,x
        lda i_pws,y
        sta pwdir,x
        lda i_vdel,y
        sta vdel,x
        lda i_vspd,y
        lsr
        sta vcount,x
        lda blocked,x
        bne +
        lda i_ad,y
        pha
        lda i_sr,y
        ldy sidoff,x
        sta SID+6,y
        pla
        sta SID+5,y
+       rts

; ---------------------------------------------------------------------------
; run the instrument program for one frame and write the voice registers
update
        ; wave/note program step
        ldy wtpos,x
        lda wt_wave,y
        sta ctrl,x
        lda wt_note,y
        bmi abs
        clc
        adc note,x
        jmp setf
abs     and #$7f
setf    tay
        lda freqlo,y
        sta flo,x
        lda freqhi,y
        sta fhi,x
        ldy wtpos,x
        lda wt_next,y
        sta wtpos,x

        ; vibrato (triangle, centred on the note)
        ldy inst,x
        lda i_vdep,y
        beq novib
        lda vdel,x
        beq dovib
        dec vdel,x
        jmp novib
dovib   lda vdir,x
        bne vdown
        clc
        lda voffl,x
        adc i_vdep,y
        sta voffl,x
        lda voffh,x
        adc #0
        sta voffh,x
        jmp vstep
vdown   sec
        lda voffl,x
        sbc i_vdep,y
        sta voffl,x
        lda voffh,x
        sbc #0
        sta voffh,x
vstep   dec vcount,x
        bne vadd
        lda i_vspd,y
        sta vcount,x
        lda vdir,x
        eor #1
        sta vdir,x
vadd    clc
        lda flo,x
        adc voffl,x
        sta flo,x
        lda fhi,x
        adc voffh,x
        sta fhi,x
novib
        ; pulse width sweep, bouncing between per-instrument limits
        lda pwdir,x
        beq pwdone
        bmi pwdown
        clc
        adc pwlo,x
        sta pwlo,x
        lda pwhi,x
        adc #0
        sta pwhi,x
        cmp i_pwmax,y
        bcc pwdone
        jmp pwflip
pwdown  clc
        adc pwlo,x
        sta pwlo,x
        lda pwhi,x
        adc #$ff
        sta pwhi,x
        cmp i_pwmin,y
        bcs pwdone
pwflip  lda pwdir,x
        eor #$ff
        clc
        adc #1
        sta pwdir,x
pwdone
        ; write registers
        lda blocked,x
        beq +
        rts
+       ldy sidoff,x
        lda flo,x
        sta SID+0,y
        lda fhi,x
        sta SID+1,y
        lda pwlo,x
        sta SID+2,y
        lda pwhi,x
        sta SID+3,y
        lda ctrl,x
        sta SID+4,y
        rts

; ---------------------------------------------------------------------------
sidoff  !byte 0, 7, 14

; voice state lives in the cassette buffer ($033C-$03FB, unused by
; PETSCII Pit) as one block, so a whole song position can be saved
vstate  = $033c
ptrlo   = vstate+0
ptrhi   = vstate+3
cnt     = vstate+6
inst    = vstate+9
note    = vstate+12
resting = vstate+15
hr      = vstate+18
ctrl    = vstate+21
wtpos   = vstate+24
flo     = vstate+27
fhi     = vstate+30
pwlo    = vstate+33
pwhi    = vstate+36
pwdir   = vstate+39
vdel    = vstate+42
vcount  = vstate+45
vdir    = vstate+48
voffl   = vstate+51
voffh   = vstate+54
blocked = vstate+57
opos    = vstate+60
trn     = vstate+63
olo     = vstate+66
ohi     = vstate+69
VSLEN   = 72
cursong = vstate+VSLEN
tmps    = cursong+1
tmpp    = cursong+2
vsave   = cursong+3
paused  = vsave+VSLEN
mood    = paused+1          ; 0 happy, 1 sad
usedd   = paused+2          ; Dungeoneering has a saved place
usedl   = paused+3          ; Lamenting has a saved place
newmd   = paused+4
!if newmd+1 > $03fc { !error "state overflows the cassette buffer" }
; Lamenting's saved place: $02A7-$02EE, free RAM the KERNAL and BASIC never use
lsave   = $02a7

        !source "music.asm"
