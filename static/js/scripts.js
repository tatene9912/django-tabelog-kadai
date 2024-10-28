document.addEventListener('DOMContentLoaded', (event) => {
    const textCropLength = 60;

    document.querySelectorAll('.js-cropText').forEach((el) => {
        console.log("Processing element:", el); // デバッグ用ログ
        const text = el.innerHTML;

        // 文字数がtextCropLength以下なら何もしない
        if (text.length <= textCropLength) return true;

        // 文字を分割する
        const text1 = text.substr(0, textCropLength);
        const text2 = text.substr(textCropLength);
        let html = '<span>' + text1 + '</span>';
        html += '<span class="more">' + text2 + '</span>';
        html += '<span class="dot">…</span>';
        el.innerHTML = html;

        // もっと見るのボタンを作成
        const showMore = document.createElement('button');
        const showMoreText = document.createTextNode('もっと見る');
        showMore.appendChild(showMoreText);

        // もっと見るのボタンに対してイベントを設定
        showMore.addEventListener('click', function(ev) {
            const self = ev.target;
            const state = self.innerHTML === 'もっと見る' ? 'close' : 'open';

            if (state === 'close') {
                self.innerHTML = '元に戻す';
                self.parentNode.querySelector('.more').style.display = 'inline';
                self.parentNode.querySelector('.dot').style.display = 'none';
            } else {
                self.innerHTML = 'もっと見る';
                self.parentNode.querySelector('.more').style.display = 'none';
                self.parentNode.querySelector('.dot').style.display = 'inline';
            }
        });
        el.appendChild(showMore);
    });
});

// notificationを×押下で閉じれるように。
for (const element of document.querySelectorAll('.notification > .delete')) {
    element.addEventListener('click', e => {
        e.target.parentElement.classList.add('is-hidden');
    });
}

// ナビバーの開閉を設定
for (const element of document.querySelectorAll('.navbar-burger')) {
    const menuId = element.dataset.target;
    const menu = document.getElementById(menuId);
    element.addEventListener('click', e => {
        element.classList.toggle('is-active');
        menu.classList.toggle('is-active');
    });
}

document.addEventListener('DOMContentLoaded', function () {
    const dateField = document.querySelector('input[name="date"]');
    const timeField = document.querySelector('select[name="time"]');
    const locationId = document.getElementById('locationId').value;

    dateField.addEventListener('change', function () {
        const date = dateField.value;

        fetch(`/reservation/create/available_times/?date=${date}&location_id=${locationId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                timeField.innerHTML = '';  // 既存の選択肢をクリア
                if (data.length === 0) {
                    const noOptions = document.createElement('option');
                    noOptions.value = '';
                    noOptions.text = '利用可能な時間がありません';
                    timeField.add(noOptions);
                } else {
                    data.forEach(function (time) {
                        const option = document.createElement('option');
                        option.value = time; // 時間を value に設定
                        option.text = time;  // 時間を表示用のテキストとして設定
                        timeField.add(option); // オプションを追加
                    });
                }
            })
            .catch(error => {
                console.error('Error fetching available times:', error);
            });
    });
});





