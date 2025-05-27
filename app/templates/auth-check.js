window.onload = function () {
    const isLoggedIn = localStorage.getItem('loggedIn');
    if (!isLoggedIn) {
        alert("로그인 후 이용 가능합니다.");

        // 절대경로 리디렉션 (항상 ECOPS_webpage 기준으로 이동)
        const redirectURL = `${window.location.origin}/ECOPS_webpage/index0.html`;
        window.location.href = redirectURL;
        return;
    }

    // 로그인 상태면 본문 표시
    document.body.style.display = "block";

    // 새로고침 시 로그아웃
    const navType = performance.getEntriesByType("navigation")[0]?.type;
    if (navType === "reload") {
        localStorage.removeItem('loggedIn');
        const redirectURL = `${window.location.origin}/ECOPS_webpage/index0.html`;
        window.location.href = redirectURL;
    }
};
