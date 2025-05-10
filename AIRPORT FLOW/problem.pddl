(define (problem aeroporto-problem)
  (:domain aeroporto)
  (:objects
    p0 - passeggero
    check1 - postazione
    security1 - security-area
    passport1 - controllo-passaporto
    gate_internazionale - gate
    gate_nazionale - gate
    personale1 - personale
  )
  (:init
    (libero personale1) 
    (ha-bagagli p0)
    (volo-internazionale p0)
    (gate-nazionale gate_nazionale)
  )
  (:goal (and
    (imbarcato p0)
  ))
)