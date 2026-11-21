(function () {
    "use strict";

    function setError(errorEl, message) {
        if (!errorEl) {
            return;
        }
        if (!message) {
            errorEl.textContent = "";
            errorEl.hidden = true;
            return;
        }
        errorEl.textContent = message;
        errorEl.hidden = false;
    }

    async function fetchCsrfToken(csrfEndpoint) {
        const response = await fetch(csrfEndpoint, {
            method: "GET",
            credentials: "same-origin",
        });
        if (!response.ok) {
            throw new Error("Gagal mengambil token keamanan.");
        }
        const data = await response.json();
        return data.csrf_token;
    }

    function bindAuthForm(form) {
        const errorEl = form.parentElement
            ? form.parentElement.querySelector("[data-auth-error]")
            : null;
        const submitBtn = form.querySelector("[data-submit-btn]");

        form.addEventListener("submit", async function (event) {
            event.preventDefault();
            setError(errorEl, "");

            const formData = new FormData(form);
            const email = String(formData.get("email") || "").trim();
            const password = String(formData.get("password") || "");

            if (submitBtn) {
                submitBtn.disabled = true;
            }

            try {
                const csrfToken = await fetchCsrfToken(form.dataset.csrfEndpoint);
                const response = await fetch(form.dataset.endpoint, {
                    method: "POST",
                    credentials: "same-origin",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRF-Token": csrfToken,
                    },
                    body: JSON.stringify({ email: email, password: password }),
                });

                const payload = await response.json().catch(function () {
                    return {};
                });

                if (!response.ok) {
                    setError(errorEl, payload.error || "Permintaan gagal diproses.");
                    return;
                }

                window.location.assign(form.dataset.redirect || "/");
            } catch (err) {
                setError(errorEl, "Terjadi gangguan koneksi ke server.");
            } finally {
                if (submitBtn) {
                    submitBtn.disabled = false;
                }
            }
        });
    }

    function bindLogoutButton(button) {
        const container = button.closest(".dashboard-card");
        const errorEl = container ? container.querySelector("[data-auth-error]") : null;

        button.addEventListener("click", async function () {
            setError(errorEl, "");
            button.disabled = true;

            try {
                const csrfToken = await fetchCsrfToken(button.dataset.csrfEndpoint);
                const response = await fetch(button.dataset.endpoint, {
                    method: "POST",
                    credentials: "same-origin",
                    headers: {
                        "X-CSRF-Token": csrfToken,
                    },
                });

                if (!response.ok) {
                    setError(errorEl, "Gagal keluar dari sesi.");
                    return;
                }

                window.location.assign(button.dataset.redirect || "/login");
            } catch (err) {
                setError(errorEl, "Terjadi gangguan koneksi ke server.");
            } finally {
                button.disabled = false;
            }
        });
    }

    document.querySelectorAll("[data-auth-form]").forEach(bindAuthForm);
    document.querySelectorAll("[data-logout-btn]").forEach(bindLogoutButton);
})();
