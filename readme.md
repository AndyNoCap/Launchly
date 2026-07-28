[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![C++20](https://img.shields.io/badge/C%2B%2B-20-00599C?logo=cplusplus)](https://isocpp.org/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)](https://github.com)
[![Build Status](https://img.shields.io/badge/Build-Passing-brightgreen)](https://github.com)

Launchly Physics Hub este un laborator virtual interactiv dezvoltat pentru simularea, vizualizarea și înțelegerea intuitivă a fenomenelor fizice. Platforma reunește 14 module interactive de fizică clasică și modernă, oferind un mediu educațional imersiv, performant și intuitiv.

Despre Proiect

Platforma elimină barierele dintre teorie și practică. Utilizatorii pot regla în timp real parametri precum masa, viteza, unghiul de lansare, coeficienții de frecare, constantele elastice, sarcinile electrice și viteza luminii, observând instantaneu consecințele fizice prin randare grafică de înaltă precizie (60+ FPS).

Caracteristici Cheie
14 Laboratoare Interactive: Acoperă mecanica, astrofizica, optica, electrocinetica, termodinamica, undele și relativitatea.
Sistem Integrat de Evaluare (Quiz & Feedback): Teste grilă și probleme cu feedback explicativ pas cu pas în caz de răspuns incorect.
Interfață Modernă Dark Theme: Design responsive adaptat pentru ecrane de la HD până la 4K.
Motor Fizic Decuplat (MVC): Calcul matematic precis bazat pe integratori numerici (Euler-Cromer / Runge-Kutta).
Configurație Extensibilă (JSON): Suport facil pentru adăugarea de noi experimente și scenarii fără recompilare.

Tehnologii & Arhitectură

Aplicația folosește o arhitectură Model-View-Controller (MVC) complet decuplată:

Model (Physics Core Engine): C++20 / Python - Gestionează modelele matematice și integrările numerice independent de GUI.
View (UI & Rendering): Pygame / Custom Vector Rendering System - Se ocupă de desenarea cadrelor și controlul interfeței la 60 FPS.
Controller (Event Manager): Intermediază evenimentele de la tastatură/mouse (sliders, drag-and-drop) către starea fizică.

Cerințe de Sistem

| Componentă | Minim | Recomandat 

|OS| Windows 10 (64-bit), Linux (Ubuntu 20.04+), macOS 11+ | Windows 11 / macOS 13+ |
|CPU| Dual-Core 2.0 GHz | Quad-Core 3.0 GHz+ |
|RAM| 2 GB | 4 GB |
|Grafică| Suport OpenGL 3.3 | GPU integrat/dedicat modern |
|Stocare| 150 MB spațiu liber | 500 MB spațiu liber |


Instalare și Rulare

1. Mergi la secțiunea [Releases](../../releases).
2. Descărcă `Launchly_Physics_Hub_v1.0.zip` pentru sistemul tău de operare.
3. Extrage arhiva și rulează executabilul `Launchly_Physics_Hub.exe` (sau `./Launchly_Physics_Hub` pe Linux/macOS).

Cerințe prealabile:
* Python 3.10+ (sau compilator C++20 cu CMake 3.20+)
* Git


Licență și Contribuții

Acest proiect este distribuit sub licența **MIT**. Consultați fișierul [LICENSE](LICENSE) pentru mai multe detalii.

Contribuțiile sunt binevenite! Vă rugăm să deschideți un *Issue* sau un *Pull Request* pentru sugestii de funcționalități noi sau îmbunătățiri.


 *Dacă îți place proiectul, oferă-i un star pe GitHub!*