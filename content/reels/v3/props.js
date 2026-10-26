// Gancho: o carimbo já está lá; a janela sai em perspectiva quando a narração vira
tl.fromTo("#hookwin", { rotationX: 8, y: 20 }, { rotationX: 0, y: 0, duration: 1.2, ease: "expo.out" }, 0);
tl.to("#hookwin", { x: -900, rotationY: -25, opacity: 0, duration: 0.45, ease: "power3.in" }, {{T:show~0.1}});

// Janela do chat: entra pela direita, digita o pedido, recebe a resposta e leva o carimbo
tl.fromTo("#chatwin", { x: 900, rotationY: 25, opacity: 0 }, { x: 0, rotationY: 0, opacity: 1, duration: 0.55, ease: "expo.out" }, {{T:ask~0.1}});
tl.fromTo("#ask", { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.3, ease: "expo.out" }, {{T:ask+0.45}});
tl.fromTo("#ans .a", { opacity: 0 }, { opacity: 1, duration: 0.1, stagger: 0.05 }, {{T:resp}});
tl.fromTo("#chatstamp", { scale: 2.2, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.25, ease: "back.out(1.6)" }, {{T:resp_end+0.05}});
tl.to("#chatwin", { scale: 0.92, y: -20, duration: 0.5, ease: "power2.inOut" }, {{T:think}});
tl.to("#chatwin", { x: -900, rotationY: -25, opacity: 0, duration: 0.45, ease: "power3.in" }, {{T:parts~0.15}});

// As 4 partes: entram em cascata e acendem uma a uma quando narradas
tl.fromTo("#chips .chip", { y: 80, opacity: 0, scale: 0.9 }, { y: 0, opacity: 1, scale: 1, duration: 0.45, ease: "expo.out", stagger: 0.12 }, {{T:quatro}});
["p1", "p2", "p3", "p4"].forEach((p, i) => {
  const id = "#ch" + (i + 1);
  tl.to(id, { borderColor: "#D9480F", scale: 1.04, boxShadow: "0 24px 60px rgba(217,72,15,.25)", duration: 0.25, ease: "power2.out" }, T[p]);
  tl.to(id, { borderColor: "rgba(0,0,0,0)", scale: 1, boxShadow: "0 16px 50px rgba(18,18,17,.10)", duration: 0.25 }, T[p + "_end"] + 0.1);
});
tl.to("#chips", { x: -900, rotationY: -25, opacity: 0, duration: 0.45, ease: "power3.in" }, {{T:diff~0.15}});

// Resposta boa
tl.fromTo("#good", { x: 900, rotationY: 25, opacity: 0 }, { x: 0, rotationY: 0, opacity: 1, duration: 0.55, ease: "expo.out" }, {{T:diff}});
tl.fromTo("#good .cap", { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.3, stagger: 0.25, ease: "expo.out" }, {{T:diff+0.4}});
tl.fromTo("#okbadge", { scale: 0.3, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.3, ease: "back.out(1.8)" }, {{T:diff_end+0.1}});
tl.to(["#good", "#okbadge"], { x: -900, rotationY: -25, opacity: 0, duration: 0.45, ease: "power3.in" }, {{T:cta~0.15}});

// Chamada: digita a palavra, publica, DM sai
tl.fromTo("#cbox", { y: 60, opacity: 0 }, { y: 0, opacity: 1, duration: 0.45, ease: "expo.out" }, {{T:cta}});
tl.fromTo("#cbox .k", { opacity: 0 }, { opacity: 1, duration: 0.01, stagger: 0.07 }, {{T:kw~0.2}});
tl.to("#pub1", { opacity: 0, duration: 0.1 }, {{T:kw+0.6}});
tl.to("#pub2", { opacity: 1, duration: 0.15 }, {{T:kw+0.6}});
tl.to("#caret", { opacity: 0, duration: 0.05 }, {{T:kw+0.6}});
tl.fromTo(["#dmlabel", "#dmpill"], { y: 40, opacity: 0 }, { y: 0, opacity: 1, duration: 0.4, ease: "expo.out", stagger: 0.08 }, {{T:dm}});
tl.fromTo("#dmnote", { opacity: 0 }, { opacity: 1, duration: 0.3 }, {{T:dm+0.5}});
