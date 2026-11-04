(function () {
    "use strict";

    const endpoint = "/notifications/updates";
    const list = document.querySelector(".notification-list");
    let lastId = list ? Number(list.dataset.lastId || 0) : 0;
    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content || "";

    function updateBadges(count) {
        document.querySelectorAll("a[href]").forEach((anchor) => {
            let path = "";
            try {
                path = new URL(anchor.href, window.location.href).pathname;
            } catch (_) {
                return;
            }
            if (!path.endsWith("/notifications")) return;

            let badge = anchor.querySelector("[data-notification-badge]");
            if (count > 0) {
                if (!badge) {
                    badge = document.createElement("span");
                    badge.dataset.notificationBadge = "true";
                    badge.style.cssText = "position:absolute;top:-3px;right:-4px;min-width:18px;height:18px;padding:0 3px;display:flex;align-items:center;justify-content:center;border-radius:999px;background:#dc2626;color:#fff;font-size:10px;line-height:1;font-weight:800;border:2px solid #fff;";
                    anchor.style.position = "relative";
                    anchor.appendChild(badge);
                }
                badge.textContent = count < 100 ? String(count) : "99+";
            } else if (badge) {
                badge.remove();
            }
        });
    }

    function appendNotification(item) {
        let targetList = document.querySelector(".notification-list");
        const emptyState = document.querySelector(".empty-state");
        if (!targetList) {
            targetList = document.createElement("section");
            targetList.className = "notification-list";
            targetList.setAttribute("aria-label", "Your notifications");
            if (emptyState) {
                emptyState.replaceWith(targetList);
            } else {
                const main = document.querySelector("main");
                if (main) main.appendChild(targetList);
            }
        }

        const card = document.createElement("article");
        card.className = "notification-card unread";

        const icon = document.createElement("div");
        icon.className = "notification-icon";
        icon.setAttribute("aria-hidden", "true");
        icon.textContent = "!";
        card.appendChild(icon);

        const content = document.createElement("div");
        content.className = "notification-content";

        const heading = document.createElement("h3");
        heading.textContent = item.message;
        const fresh = document.createElement("span");
        fresh.className = "unread-badge";
        fresh.textContent = "NEW";
        heading.appendChild(document.createTextNode(" "));
        heading.appendChild(fresh);
        content.appendChild(heading);

        const description = document.createElement("p");
        description.textContent = item.label;
        content.appendChild(description);

        const meta = document.createElement("div");
        meta.className = "notification-meta";
        const type = document.createElement("span");
        type.className = "type-badge";
        type.textContent = item.label;
        const date = document.createElement("span");
        date.className = "notification-date";
        date.textContent = item.created_at;
        meta.append(type, date);
        content.appendChild(meta);

        const actions = document.createElement("div");
        actions.className = "notification-actions";
        const form = document.createElement("form");
        form.method = "POST";
        form.action = "/notification/open/" + encodeURIComponent(item.id);
        const token = document.createElement("input");
        token.type = "hidden";
        token.name = "csrf_token";
        token.value = csrfToken;
        const button = document.createElement("button");
        button.type = "submit";
        button.className = "primary";
        button.textContent = item.type === "match_message"
            ? "Open Private Chat"
            : item.match_id
                ? "Open My Matches"
                : item.type === "blood_request"
                    ? "View Available Requests"
                    : item.request_id
                        ? "View My Requests"
                        : item.type === "eligibility"
                            ? "View Donor Profile"
                            : "Open Dashboard";
        form.append(token, button);
        actions.appendChild(form);
        content.appendChild(actions);
        card.appendChild(content);
        targetList.prepend(card);
        targetList.dataset.lastId = String(item.id);
    }

    async function refreshNotifications() {
        try {
            const response = await fetch(endpoint + "?after_id=" + lastId, {
                credentials: "same-origin",
                headers: { "Accept": "application/json" }
            });
            if (response.status === 401 || response.status === 403) return;
            if (!response.ok) return;
            const data = await response.json();
            if (!data.ok) return;

            updateBadges(Number(data.unread_count || 0));
            const count = document.querySelector(".notification-count");
            if (count) {
                count.textContent = Number(data.unread_count || 0)
                    + " unread · " + Number(data.total_count || 0) + " total";
            }

            if (Array.isArray(data.notifications)) {
                data.notifications.forEach((item) => {
                    appendNotification(item);
                    lastId = Math.max(lastId, Number(item.id || 0));
                });
            }
        } catch (_) {
            // Keep the current page usable when background polling is offline.
        }
    }

    refreshNotifications();
    window.setInterval(refreshNotifications, 12000);
})();
