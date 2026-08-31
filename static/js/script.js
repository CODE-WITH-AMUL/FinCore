// its the main landing page script file
window.addEventListener("load", () => {
        const pl = document.getElementById("preloader");
        setTimeout(() => {
          pl.classList.add("hidden");
          document.body.classList.remove("loading");
        }, 400);
      });



      const io = new IntersectionObserver(
        (entries) => {
          entries.forEach((e) => {
            if (e.isIntersecting) e.target.classList.add("in-view");
          });
        },
        { threshold: 0.15 },
      );
      document
        .querySelectorAll(
          ".cap, .insight-card, .section-head, .problem-item, .dash-mock",
        )
        .forEach((el) => io.observe(el));

      const navLinks = document.querySelectorAll("#navlinks a");
      const sections = [...navLinks]
        .map((a) => document.getElementById(a.dataset.nav))
        .filter(Boolean);
      const spy = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              navLinks.forEach((a) =>
                a.classList.toggle("active", a.dataset.nav === entry.target.id),
              );
            }
          });
        },
        { rootMargin: "-45% 0px -50% 0px" },
      );
      sections.forEach((s) => spy.observe(s));