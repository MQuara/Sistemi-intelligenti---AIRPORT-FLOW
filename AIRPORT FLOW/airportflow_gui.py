import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import subprocess
import tkinter as tk
from tkinter import messagebox, simpledialog

# === CONFIG ===
ENHSP_PATH = "enhsp.jar"
DOMAIN_FILE = "domain.pddl"
PROBLEM_FILE = "problem.pddl"
PLAN_FILE = "plan.txt"

# === GLOBAL VAR ===
num_checkin = 0
num_security = 0
num_passport = 0
num_personale = 0
nomi = {}
passeggeri = []
passenger_colors = {}
passenger_bagagli = {}
bagagli_circle = {}
positions = {
    "personale-libero": (-2,8),
    "fuori": (-3,5),
    "ingresso": (-2, 5),
    "check_exit": (1, 5.5),
    "security_exit": (4, 5.5),
    "passport_exit": (7, 5.5),
    "gate_internazionale": (12, 7.5),
    "gate_nazionale": (12, 5.5),
    "aereo_nazionale":(14, 5.5),
    "aereo_internazionale":(14, 7.5),
    "airside": (10, 7),
    "finito_nazionale":(13, 5.5),
    "finito_internazionale":(13, 7.5),
}
colori = ['red', 'silver', 'blue', 'yellow', 'orange', 'purple', 'pink', 'brown', 'black', 'cyan', 'magenta']


# === APRI FINESTRA CONFIGURAZIONE ===
def apri_finestra():
    root = tk.Tk()
    root.title("Configurazione Simulazione Aeroporto")

    frame = tk.Frame(root)
    frame.pack(padx=10, pady=10)

    def chiedi_passeggeri():
        global passeggeri
        passeggeri.clear()
        n = simpledialog.askinteger("Passeggeri", "Quanti passeggeri?", minvalue=1)
        if n is not None and n>0:
            for i in range(n):
                nome = simpledialog.askstring("Nome passeggero", f"Nome passeggero {i+1}:", initialvalue="")
                bagagli = messagebox.askyesno("Bagagli", f"{nome} ha bagagli da stiva?")
                internazionale = messagebox.askyesno("Volo Internazionale", f"{nome} ha un volo internazionale?")
                passeggeri.append((
                    nome.lower() if nome else f"p{i}",
                    bagagli if bagagli else False,
                    internazionale if internazionale else False
                ))
    
    tk.Button(frame, text="Imposta passeggeri", command=chiedi_passeggeri).grid(row=0, column=0, pady=5)

    checkin_var = tk.IntVar(value=1)
    tk.Label(frame, text="Numero postazioni check-in:").grid(row=1, column=0, sticky="w")
    tk.Entry(frame, textvariable=checkin_var).grid(row=1, column=1)

    security_var = tk.IntVar(value=1)
    tk.Label(frame, text="Numero postazioni security:").grid(row=2, column=0, sticky="w")
    tk.Entry(frame, textvariable=security_var).grid(row=2, column=1)

    passport_var = tk.IntVar(value=1)
    tk.Label(frame, text="Numero postazioni controllo passaporto:").grid(row=3, column=0, sticky="w")
    tk.Entry(frame, textvariable=passport_var).grid(row=3, column=1)

    personale_var = tk.IntVar(value=1)
    tk.Label(frame, text="Numero personale:").grid(row=5, column=0, sticky="w")
    tk.Entry(frame, textvariable=personale_var).grid(row=5, column=1)

    

    def conferma():
        if not passeggeri:
            messagebox.showerror("Errore", "Prima devi impostare i passeggeri.")
            return
        global num_checkin 
        num_checkin = checkin_var.get()
        global num_security 
        num_security = security_var.get()
        global num_passport 
        num_passport = passport_var.get()
        global num_personale
        num_personale = personale_var.get()
        #print(num_checkin)
        salva_e_avvia(
            passeggeri,
            checkin_var.get(),
            security_var.get(),
            passport_var.get(),
            personale_var.get()
        )
        root.destroy()

    tk.Button(frame, text="Genera e Simula", command=conferma, bg="green", fg="white").grid(row=6, columnspan=2, pady=10)
    root.mainloop()

# === GENERA FILE PROBLEM.PDDL ===
def genera_problem_pddl(passeggeri, num_checkin, num_security, num_passport, num_personale):
    problem = "(define (problem aeroporto-problem)\n"
    problem += "  (:domain aeroporto)\n"
    problem += "  (:objects\n"

    for p in passeggeri:
        problem += f"    {p[0]} - passeggero\n"
    for i in range(1, num_checkin + 1):
        problem += f"    check{i} - postazione\n"
    for i in range(1, num_security + 1):
        problem += f"    security{i} - security-area\n"
    for i in range(1, num_passport + 1):
        problem += f"    passport{i} - controllo-passaporto\n"
    problem += "    gate_internazionale - gate\n"
    problem += "    gate_nazionale - gate\n"
    for i in range(1, num_personale + 1):
        problem += f"    personale{i} - personale\n"

    problem += "  )\n  (:init\n"
    for i in range(1, num_personale + 1):
        problem += f"    (libero personale{i}) \n"
    for p in passeggeri:
        if p[1]:
            problem += f"    (ha-bagagli {p[0]})\n"
        if p[2]:
            problem += f"    (volo-internazionale {p[0]})\n"
    problem += f"    (gate-nazionale gate_nazionale)\n"
    problem += "  )\n  (:goal (and\n"
    for p in passeggeri:
        problem += f"    (imbarcato {p[0]})\n"
    problem += "  ))\n)"
    
    return problem

# === SALVA FILE PROBLEM.PDDL E AVVIA ===
def salva_e_avvia(passeggeri, num_checkin, num_security, num_passport, num_personale):
    contenuto = genera_problem_pddl(passeggeri, num_checkin, num_security, num_passport, num_personale)
    with open(PROBLEM_FILE, "w") as f:
        f.write(contenuto)

# === ESEGUI ENHSP ===
def run_enhsp(algoritmo):
    print("Eseguo ENHSP...")
    if (algoritmo == "opt"):
        #print("opt")
        cmd = [
            "java", "-jar", ENHSP_PATH,
            "-o", DOMAIN_FILE,
            "-f", PROBLEM_FILE,
            "-planner", "opt-hrmax"
        ]
    elif (algoritmo == "sub-opt"):
        #print("sub-opt")
        cmd = [
            "java", "-jar", ENHSP_PATH,
            "-o", DOMAIN_FILE,
            "-f", PROBLEM_FILE,
            "-planner", "sat-hadd"
        ]
    else:
        #print("non opt")
        cmd = [
            "java", "-jar", ENHSP_PATH,
            "-o", DOMAIN_FILE,
            "-f", PROBLEM_FILE,
        ]
    #print(cmd)
    with open(PLAN_FILE, "w") as outfile:
        subprocess.run(cmd, stdout=outfile)
    print("Pianificazione completata.")

# === PARSE PLAN ===
def parse_plan():
    actions = []
    in_plan = False
    with open(PLAN_FILE, "r") as f:
        for line in f:
            if "Found Plan" in line:
                in_plan = True
                continue
            if in_plan and line.strip() and line[0].isdigit():
                tokens = line.split(":", 1)[1].strip().lower().replace("(", "").replace(")", "").split()
                actions.append(tokens)
    #print(actions)
    return actions

# === ANIMA PLAN ===
def animate_plan(actions):
    if not passeggeri: 
        return
    fig, ax = plt.subplots()
    # Cornice che racchiude tutto
    cornice = plt.Rectangle((-2.8, 0.2), 15.5, 13.8, edgecolor='black', facecolor='none', lw=2)
    ax.add_patch(cornice)

    ax.set_xlim(-4, 15)
    ax.set_ylim(0, 14)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("✈️ Airport flow", fontsize=16, fontweight='bold', pad=20)

    airside = plt.Rectangle((9, 5), 2, 3, edgecolor='orange', facecolor='lightyellow', alpha=0.3, lw=2)
    ax.add_patch(airside)
    ax.text(10, 8.7, "Airside", ha="center", va="center", fontsize=12, color="darkorange", weight="bold")
    ax.text(14,7,"✈️",fontsize=50)
    ax.text(14,5,"✈️",fontsize=50)
    n=0
    while n < num_checkin:
        positions[f"check{n+1}"] = (0,n*2+1)
        n +=1
    n=0
    while n < num_security:
        positions[f"security{n+1}"] = (3,14-(n*2+1))
        n +=1
    n=0
    while n < num_passport:
        positions[f"passport{n+1}"] = (6,n*2+1)
        n +=1
    #print(positions)
    for name, pos in positions.items():
        if "exit" in name or name == "airside" or name == "fuori" or name == "aereo_nazionale" or name == "aereo_internazionale" or name == "finito_internazionale" or name == "finito_nazionale":
            continue
        #ax.plot(pos[0], pos[1], "b^", markersize=10)
        if "check" in name:
            ax.add_patch(patches.FancyBboxPatch(
            (pos[0]-0.5, pos[1]-0.4), 1, 0.8,
            boxstyle="round,pad=0.1", edgecolor='gray', facecolor="#d4edda", lw=1.5, alpha=0.9))
        elif "security" in name:
            ax.add_patch(patches.FancyBboxPatch(
            (pos[0]-0.5, pos[1]-0.4), 1, 0.8,
            boxstyle="round,pad=0.1", edgecolor='gray', facecolor="#d1ecf1", lw=1.5, alpha=0.9))
        elif "passport" in name:
            ax.add_patch(patches.FancyBboxPatch(
            (pos[0]-0.5, pos[1]-0.4), 1, 0.8,
            boxstyle="round,pad=0.1", edgecolor='gray', facecolor="#f8d7da", lw=1.5, alpha=0.9))
        else:
            ax.add_patch(patches.FancyBboxPatch(
            (pos[0]-0.5, pos[1]-0.4), 1, 0.8,
            boxstyle="round,pad=0.1", edgecolor='gray', facecolor="#e2e3f3", lw=1.5, alpha=0.9))
        ax.text(pos[0], pos[1] + 0.8, name, ha="center",fontsize=9, fontweight='bold', color="black")

    for p in passeggeri:
        pos = positions["fuori"]
        passenger_colors[f"{p[0]}"]=f"{(random.choice(colori))}"
        if p[1] is True:
            passenger_bagagli[f"{p[0]}"]= "si"
            bagagli_circle[f"{p[0]}"]= plt.Circle((pos[0]-0.2,pos[1]), 0.08, color='#fce4ec')

    passenger_circles = {}
    passenger_positions = {}
    for p in passenger_colors:
        pos = positions["fuori"]
        circle = plt.Circle(pos, 0.15, color=passenger_colors[p])
        nomi[f"{p}"] = ax.text(pos[0], pos[1] + 0.4, f'{p}', color='black', ha='center', va='center')
        ax.add_patch(circle)
        if p in passenger_bagagli:
            ax.add_patch(bagagli_circle[f"{p}"])
        passenger_circles[p] = circle
        passenger_positions[p] = pos

    personale_positions = {}
    nomi_personale = {}
    personale_circles = {}

    j = 1
    global num_personale
    while j <= num_personale:
        pos = positions["personale-libero"]
        square = patches.Rectangle((pos[0] - 0.15, pos[1] - 0.15), 0.3, 0.3,
                               facecolor=f"{(random.choice(colori))}", edgecolor="black", alpha=0.8)
        #circle = plt.Circle(pos, 0.15, color=f"{(random.choice(colori))}")
        nomi_personale[f"personale{j}"] = ax.text(pos[0], pos[1] + 0.4, f'personale{j}', color='black', ha='center', va='center')
        ax.add_patch(square)
        personale_circles[f"personale{j}"] = square
        personale_positions[f"personale{j}"] = pos
        j += 1
    #print(personale_positions)
    
    def move_passenger(p, target):
        if target not in positions: return
        start, end = passenger_positions[p], positions[target]
        for i in range(20):
            x = start[0] + (end[0] - start[0]) * i / 20
            y = start[1] + (end[1] - start[1]) * i / 20
            passenger_circles[p].center = (x, y)
            nomi[f"{p}"].set_position((x,y + 0.4))
            if p in passenger_bagagli:
                bagagli_circle[f"{p}"].center = ((x-0.2),y)
            fig.canvas.draw()
            plt.pause(0.03)
        passenger_positions[p] = end

    def move_personale(p, target):
        if target not in positions: return
        start, end = personale_positions[p], positions[target]
        for i in range(25):
            x = start[0] + (end[0] - start[0]) * i / 25
            y = start[1] + (end[1] - start[1]) * i / 25
            personale_circles[p].set_xy((x, y))
            nomi_personale[f"{p}"].set_position((x,y + 0.4))
            fig.canvas.draw()
            plt.pause(0.03)
        personale_positions[p] = end

    movement_map = {
        "vai-checkin",
        "vai-sicurezza",
        "vai-controllo-passaporto",
        "controllo-finale-documenti",
    }

    exit_map = {
        "verifica-documenti-viaggio": "check_exit",
        "controllo-sicurezza": "security_exit",
        "passa-controllo-passaporto": "passport_exit",
        "entra-airside": "airside"
    }

    movement_map_personale = {
        "assegna-postazione",
        "libera-postazione"
    }

    additional_passenger_actions = {
        "arriva-aeroporto",
        "consegna-bagaglio-stiva",
        "controllo-gate-info",
        "aspetta-gate",
        "imbarco",
    }


    for action in actions:
        act = action[0]
        if act in movement_map:
            p = action[1]
            dest = action[2]
            #print(f"{dest} \n")
            move_passenger(p, dest)
            if act == "controllo-finale-documenti":
                if action[2] == "gate_nazionale":
                    move_passenger(p, "finito_nazionale")
                elif action[2] == "gate_internazionale":
                    move_passenger(p, "finito_internazionale")
            
        elif act in exit_map:
            if act != "entra-airside":
                p = action[1]
                passenger_circles[p].set_color("lime")
                fig.canvas.draw()
                plt.pause(1)
                passenger_circles[p].set_color(passenger_colors[p])
            move_passenger(action[1], exit_map[act])
        elif act in movement_map_personale:
            if act == "assegna-postazione":
                move_personale(action[2], action[1])
            if act == "libera-postazione":
                move_personale(action[2], "personale-libero")
        elif act in additional_passenger_actions:
            p = action[1]
            # Posizione target in base al tipo di azione
            if act == "arriva-aeroporto":
                move_passenger(p, "ingresso")
            elif act == "consegna-bagaglio-stiva":
                del passenger_bagagli[f"{p}"]
            elif act == "controllo-gate-info":
                passenger_circles[p].set_color("gold")
                fig.canvas.draw()
                plt.pause(1)
                passenger_circles[p].set_color(passenger_colors[p])
            elif act == "aspetta-gate":
                pos_testo = passenger_positions[p]
                temp = ax.text(pos_testo[0],pos_testo[1],"sto aspettando")
                fig.canvas.draw()
                plt.pause(1)
                temp.remove()
                fig.canvas.draw()
            elif act == "imbarco":
                if action[2] == "gate_nazionale":
                    move_passenger(p, "aereo_nazionale")
                elif action[2] == "gate_internazionale":
                    move_passenger(p, "aereo_internazionale")

                



    plt.show()

import click
@click.command()
@click.option('-a', '--algoritmo', default = None, help = "Scrivere 'opt' se si vuole l'algoritmo ottimale, \n'sub-opt' se si vuole l'algoritmo sub-ottimale")
def main(algoritmo):
    apri_finestra()
    run_enhsp(algoritmo)
    plan = parse_plan()
    animate_plan(plan)

if __name__ == '__main__':
    main()

    
