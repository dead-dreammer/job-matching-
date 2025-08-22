

document.addEventListener("DOMContentLoaded", () => {
    const logoutBtn = document.getElementById("logoutBtn");
    if (logoutBtn) {
        logoutBtn.addEventListener("click", async (e) => {
            e.preventDefault();
            console.log("Logout button clicked");

            try {
                const res = await fetch("/auth/logout", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                });

                const data = await res.json();
                if (data.success) {
                    console.log("Logout successful, reloading...");
                    window.location.href = "/";
                } else {
                    console.warn("Logout failed:", data);
                }
            } catch (err) {
                console.error("Logout fetch error:", err);
            }
        });
    }
});
