(define (domain airport-flow)
  (:requirements :strips :typing)

  (:types
    passeggero
    postazione security-area controllo-passaporto gate - location
    personale
  )

  (:predicates
    (arrivato ?p - passeggero)
    (check-in-fatto ?p - passeggero)
    (ha-bagagli ?p - passeggero)
    (bagaglio-consegnato ?p - passeggero)
    (documento-verificato ?p - passeggero)
    (controllo-sicurezza-superato ?p - passeggero)
    (passaporto-controllato ?p - passeggero)
    (in-airside ?p - passeggero)
    (conosce-gate ?p - passeggero)
    (at ?p - passeggero ?loc - location) ;; Dove si trova il passeggero (postazione, security-area, controllo-passaporto, gate)
    (at-ingresso ?p - passeggero)
    (aspetta-imbarco ?p - passeggero)
    (pronto-imbarco ?p - passeggero)
    (imbarcato ?p - passeggero)

    (volo-internazionale ?p - passeggero)
    (gate-assegnato ?p - passeggero ?g - gate)
    (postazione-occupata ?c - postazione)
    (postazione-passaporto-occupata ?pc - controllo-passaporto)
    (postazione-sicurezza-occupata ?s - security-area)
    (libero ?per - personale)
    (assegnato ?per - personale ?loc - location)
    (gate-nazionale ?g - gate)
    (postazione-assegnata ?loc - location)
  )

  ;; Arrivo all'aeroporto
  (:action arriva-aeroporto
    :parameters (?p - passeggero)
    :precondition (not (arrivato ?p))
    :effect (and
      (arrivato ?p)
      (at-ingresso ?p)
    )
  )

  (:action assegna-postazione
      :parameters (?loc - location ?per - personale)
      :precondition (and 
        (not(postazione-assegnata ?loc))
        (libero ?per)
        (not (assegnato ?per ?loc))
      )
      :effect (and 
        (not (libero ?per))
        (assegnato ?per ?loc)
        (postazione-assegnata ?loc)
      )
  )
  
  (:action libera-postazione
      :parameters (?loc - location ?per - personale)
      :precondition (and 
        (postazione-assegnata ?loc)
        (not (libero ?per))
        (assegnato ?per ?loc)
        (not (postazione-occupata ?loc))
      )
      :effect (and 
        (libero ?per)
        (not (assegnato ?per ?loc))
        (not(postazione-assegnata ?loc))
      )
  )

  ;; Check-in al banco
  (:action vai-checkin
    :parameters (?p - passeggero ?c - postazione ?per - personale)
    :precondition (and
      (not (postazione-occupata ?c))
      (not (check-in-fatto ?p))
      (assegnato ?per ?c)
      (at-ingresso ?p)
    )
    :effect (and
      (not (at-ingresso ?p))
      (at ?p ?c)
      (postazione-occupata ?c)
    )
  )

  ;; Bag drop (solo se ha bagaglio da stiva)
  (:action consegna-bagaglio-stiva
    :parameters (?p - passeggero ?c - postazione ?per - personale)
    :precondition (and
      (assegnato ?per ?c)
      (at ?p ?c)
      (ha-bagagli ?p)
      (not (bagaglio-consegnato ?p))
    )
    :effect (and
      (bagaglio-consegnato ?p)
    )
  )

  ;; Controllo documenti di viaggio
  (:action verifica-documenti-viaggio
    :parameters (?p - passeggero ?c - postazione ?per - personale)
    :precondition (and
      (or
        (not (ha-bagagli ?p))
        (bagaglio-consegnato ?p)
      )
      (at ?p ?c)
      (not (documento-verificato ?p))
      (assegnato ?per ?c)
    )
    :effect (and
      (documento-verificato ?p)
      (not(postazione-occupata ?c))
      (check-in-fatto ?p)
      (not (at ?p ?c))
    )
  )

  ;; Andare al controllo sicurezza
  (:action vai-sicurezza
    :parameters (?p - passeggero ?s - security-area ?per - personale)
    :precondition (and
      (not(postazione-sicurezza-occupata ?s))
      (check-in-fatto ?p)
      (assegnato ?per ?s)
    )
    :effect (and 
      (postazione-sicurezza-occupata ?s)
      (at ?p ?s)
    )
  )

  ;; Passare il controllo sicurezza
  (:action controllo-sicurezza
    :parameters (?p - passeggero ?s - security-area ?per - personale)
    :precondition (and
      (at ?p ?s)
      (not (controllo-sicurezza-superato ?p))
      (assegnato ?per ?s)
    )
    :effect (and 
      (not(postazione-sicurezza-occupata ?s))
      (controllo-sicurezza-superato ?p)
      (not (at ?p ?s))
    )
  )

  ;; Vai al controllo passaporti (solo per voli internazionali)
  (:action vai-controllo-passaporto
    :parameters (?p - passeggero ?pc - controllo-passaporto ?per - personale)
    :precondition (and
      (not(postazione-passaporto-occupata ?pc))
      (controllo-sicurezza-superato ?p)
      (volo-internazionale ?p)
      (not (passaporto-controllato ?p))
      (assegnato ?per ?pc)
    )
    :effect (and
      (postazione-passaporto-occupata ?pc)
      (at ?p ?pc)
    )
  )
  ;; Passare il controllo passaporti (solo per voli internazionali)
  (:action passa-controllo-passaporto
    :parameters (?p - passeggero ?pc - controllo-passaporto ?per - personale)
    :precondition (and
      (at ?p ?pc)
      (not (passaporto-controllato ?p))
      (assegnato ?per ?pc)
    )
    :effect (and
      (passaporto-controllato ?p)
      (not(postazione-passaporto-occupata ?pc))
      (not (at ?p ?pc))
    )
  )

  ;; Entrare nella zona airside
  (:action entra-airside
    :parameters (?p - passeggero)
    :precondition (and
      (controllo-sicurezza-superato ?p)
      (or
        (not (volo-internazionale ?p)) ;; se non internazionale basta il controllo sicurezza
        (passaporto-controllato ?p) ;; se internazionale deve avere passaporto controllato
      )
    )
    :effect (in-airside ?p)
  )

  ;;Assegnazione dinamica gate
  (:action assegna-gate-nazionale
    :parameters (?p - passeggero ?g - gate)
    :precondition (and
      (gate-nazionale ?g)
      (not (volo-internazionale ?p))
      (in-airside ?p)
      (not (conosce-gate ?p))
      (not (gate-assegnato ?p ?g))
    )
    :effect (and
      (gate-assegnato ?p ?g)
    )
  )

  (:action assegna-gate-internazionale
    :parameters (?p - passeggero ?g - gate)
    :precondition (and
      (not(gate-nazionale ?g))
      (volo-internazionale ?p)
      (in-airside ?p)
      (not (conosce-gate ?p))
      (not (gate-assegnato ?p ?g))
    )
    :effect (and
      (gate-assegnato ?p ?g)
    )
  )

  ;; Controllo del gate
  (:action controllo-gate-info
    :parameters (?p - passeggero ?g - gate)
    :precondition (and 
      (in-airside ?p)
      (gate-assegnato ?p ?g)
    )
    :effect (conosce-gate ?p)
  )

  ;; Andare al gate
  (:action vai-gate
    :parameters (?p - passeggero ?g - gate)
    :precondition (and
      (gate-assegnato ?p ?g)
      (in-airside ?p)
      (conosce-gate ?p)
    )
    :effect (at ?p ?g)
  )

  ;; Attesa al gate
  (:action aspetta-gate
    :parameters (?p - passeggero ?g - gate)
    :precondition (and
      (gate-assegnato ?p ?g)
      (at ?p ?g)
    )
    :effect (aspetta-imbarco ?p)
  )

  ;; Controllo finale dei documenti al gate
  (:action controllo-finale-documenti
    :parameters (?p - passeggero ?g - gate ?per - personale)
    :precondition (and
      (gate-assegnato ?p ?g)
      (assegnato ?per ?g)
      (aspetta-imbarco ?p)
      (at ?p ?g)
    )
    :effect (and
      (pronto-imbarco ?p)
    )
  )

  ;; Imbarco
  (:action imbarco
    :parameters (?p - passeggero ?g - gate )
    :precondition (and
      (gate-assegnato ?p ?g)
      (pronto-imbarco ?p)
      (at ?p ?g)
    )
    :effect (and
      (imbarcato ?p)
      (not (aspetta-imbarco ?p))
      (not (at ?p ?g))
    )
  )

)
