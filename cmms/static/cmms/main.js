// Extracted JS: select2 init, validation toggles, equipment ID buttons
(function(window, document){
    // Safe guard: avoid uncaught ReferenceError if someone (or an inline script) references `skill` in the page/console.
    // This sets a harmless null on window.skill only if it's not already defined.
    try { if (typeof skill === 'undefined') { window.skill = null; } } catch(e) { /* ignore */ }
    // mapping of master work type codes -> id (populated on DOM ready)
    var masterWorkTypeMap = {};
    // mapping of id (string) -> label for user-friendly toasts
    var masterWorkTypeLabels = {};

    // Small helper to show Bootstrap 5 toasts inside #toast-container
    function showToast(title, message, delay) {
        try {
            delay = typeof delay === 'number' ? delay : 7000;
            var container = document.getElementById('toast-container');
            if (!container) return;
            var toastEl = document.createElement('div');
            toastEl.className = 'toast align-items-center text-bg-light border';
            toastEl.setAttribute('role', 'alert');
            toastEl.setAttribute('aria-live', 'assertive');
            toastEl.setAttribute('aria-atomic', 'true');
            toastEl.setAttribute('data-bs-delay', String(delay));
            toastEl.innerHTML = '\n                <div class="d-flex">\n                    <div class="toast-body">' + (message || '') + '</div>\n                    <button type="button" class="btn-close me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>\n                </div>';
            container.appendChild(toastEl);
            var bsToast = new bootstrap.Toast(toastEl, { delay: delay });
            bsToast.show();
            // remove from DOM after hidden
            toastEl.addEventListener('hidden.bs.toast', function(){ toastEl.remove(); });
        } catch (err) {
            // fail silently (suppressed showToast error)
        }
    }
    function initSelect2() {
        $('select.select2').each(function() {
            var placeholder = $(this).data('placeholder');
            if (!placeholder) {
                var firstOption = $(this).find('option:first').text().trim();
                placeholder = firstOption || 'ทั้งหมด';
            }
            if (!$(this).hasClass('select2-hidden-accessible')) {
                var ajaxUrl = $(this).data('ajax-url');
                if (ajaxUrl) {
                    // allow per-element override of dropdownParent via data-dropdown-parent
                    var dpSelector = $(this).data('dropdown-parent');
                    var dropdownParentEl = null;
                    if (dpSelector) {
                        try { dropdownParentEl = $(dpSelector); } catch(e) { dropdownParentEl = null; }
                    } else if ($(this).attr('id') === 'id_skills_select') {
                        // skills select should attach dropdown to #skills-container to avoid large gaps
                        dropdownParentEl = $('#skills-container');
                    }
                    var sel2opts = {
                        theme: 'bootstrap4',
                        width: '100%',
                        placeholder: placeholder,
                        allowClear: true,
                        ajax: {
                            url: ajaxUrl,
                            dataType: 'json',
                            delay: 250,
                            data: function(params) { return { q: params.term }; },
                            processResults: function(data) { return data; },
                            cache: true
                        },
                        minimumInputLength: 1
                    };
                    if (dropdownParentEl && dropdownParentEl.length) sel2opts.dropdownParent = dropdownParentEl;
                    // debug: log resolved dropdown parent information for troubleshooting positioning
                    try {
                        console.debug('initSelect2:', {
                            id: $(this).attr('id'),
                            ajaxUrl: ajaxUrl,
                            dpSelector: dpSelector || null,
                            dropdownParentCandidate: dpSelector || (($(this).attr('id') === 'id_skills_select') ? '#skills-container' : null),
                            dropdownParentFound: !!(dropdownParentEl && dropdownParentEl.length),
                            dropdownParentEl: dropdownParentEl
                        });
                    } catch (err) { /* ignore console errors */ }
                    $(this).select2(sel2opts).on('select2:select select2:unselect change', function(e){
                            // existing select2 select handling kept for pure select2 elements
                            var $sel = $(this);
                            var ajaxUrlNow = $sel.data('ajax-url');
                            if (ajaxUrlNow && ajaxUrlNow.indexOf('/api/search/equipment') !== -1) {
                                var data = e.params.data || {};
                                handleEquipmentSelectionData(data);
                            }
                            // update skills selected count if this is the skills select
                            try { if ($sel.attr('id') === 'id_skills_select') updateSkillsSelectedCount($sel); } catch(e){}
                        });

                    // also handle native select change events for equipment selects (non-select2)
                    $(this).on('change', function(e){
                        var $sel = $(this);
                        var ajaxUrlNow = $sel.data('ajax-url') || '';
                        if (ajaxUrlNow.indexOf('/api/search/equipment') !== -1) {
                            // try to read selected option's data attributes
                            var opt = $sel.find('option:selected');
                            var data = {};
                            try {
                                data.requires_pm = opt.data('requires_pm') || opt.attr('data-requires_pm') || false;
                                data.requires_cal = opt.data('requires_cal') || opt.attr('data-requires_cal') || false;
                            } catch(err) { data = {}; }
                            handleEquipmentSelectionData(data);
                        }
                        // update skills selected count for native selects
                        try { if ($sel.attr('id') === 'id_skills_select') updateSkillsSelectedCount($sel); } catch(e){}
                    });
                } else {
                    var dpSelector = $(this).data('dropdown-parent');
                    var dropdownParentEl = null;
                    if (dpSelector) {
                        try { dropdownParentEl = $(dpSelector); } catch(e) { dropdownParentEl = null; }
                    } else if ($(this).attr('id') === 'id_skills_select') {
                        dropdownParentEl = $('#skills-container');
                    }
                    var sel2opts = {
                        theme: 'bootstrap4',
                        width: '100%',
                        placeholder: placeholder,
                        allowClear: true
                    };
                    if (dropdownParentEl && dropdownParentEl.length) sel2opts.dropdownParent = dropdownParentEl;
                    // debug: log resolved dropdown parent information for troubleshooting positioning
                    try {
                        console.debug('initSelect2:', {
                            id: $(this).attr('id'),
                            ajaxUrl: ajaxUrl || null,
                            dpSelector: dpSelector || null,
                            dropdownParentCandidate: dpSelector || (($(this).attr('id') === 'id_skills_select') ? '#skills-container' : null),
                            dropdownParentFound: !!(dropdownParentEl && dropdownParentEl.length),
                            dropdownParentEl: dropdownParentEl
                        });
                    } catch (err) { /* ignore console errors */ }
                    $(this).select2(sel2opts).on('select2:select select2:unselect change', function(){ try { if ($(this).attr('id') === 'id_skills_select') updateSkillsSelectedCount($(this)); } catch(e){} });
                    // after init, update skills count if applicable
                    try { if ($(this).attr('id') === 'id_skills_select') updateSkillsSelectedCount($(this)); } catch(e){}
                }
            }
        });
    }

    // helper to update the skills selected count badge
    function updateSkillsSelectedCount($sel) {
        try {
            var count = 0;
            if (!$sel || !$sel.length) return;
            try { console.debug('updateSkillsSelectedCount called for', $sel.attr ? $sel.attr('id') : $sel); } catch(e){}

            // 1) Prefer $sel.val() (reliable for native selects and Select2)
            try {
                var v = $sel.val();
                if (Array.isArray(v)) { count = v.length; console.debug('count from $sel.val()', count, v); }
                else if (v !== null && typeof v !== 'undefined' && v !== '') { count = 1; console.debug('count from $sel.val() single', v); }
            } catch(e) { console.debug('error reading $sel.val()', e); }

            // 2) If still zero, prefer Select2 API data
            if (!count && typeof $sel.select2 === 'function' && $sel.hasClass('select2-hidden-accessible')) {
                try { var sel2data = $sel.select2('data') || []; count = sel2data.length; console.debug('count from select2 data', count); } catch(e) { console.debug('select2 data read failed', e); }
            }

            // 3) Fallback to option:selected
            if (!count) {
                try { count = $sel.find('option:selected').length; console.debug('count from option:selected', count); } catch(e) { console.debug('option:selected read failed', e); }
            }

            // 4) Fallback: count choices inside nearest Select2 container
            if (!count) {
                try {
                    var container = $sel.nextAll('.select2-container, .select2').first();
                    if (container && container.length) {
                        var choices = container.find('.select2-selection__choice');
                        if (choices && choices.length) { count = choices.length; console.debug('count from container choices', count); }
                    }
                } catch(e) { console.debug('container choice read failed', e); }
            }

            // 5) Global fallback: count any visible Select2 choice chips on the page
            if (!count) {
                try { var globalChoices = document.querySelectorAll('.select2-selection__choice'); if (globalChoices && globalChoices.length) { count = globalChoices.length; console.debug('count from global select2-choice count', count); } } catch(e) { /* ignore */ }
            }

            var el = document.getElementById('skills-selected-count');
            if (!el) {
                console.debug('skills-selected-count element not found');
            } else {
                var newText = '(' + String(count) + ')';
                if (el.textContent !== newText) {
                    el.classList.remove('skills-count-updated');
                    void el.offsetWidth; // reflow to restart animation
                    el.textContent = newText;
                    el.classList.add('skills-count-updated');
                }
                try { el.setAttribute('aria-label', 'จำนวนทักษะที่เลือก ' + String(count)); } catch(e){}
            }
        } catch(e) { console.debug('updateSkillsSelectedCount error', e); }
    }

    // expose for debugging/testing from console
    try { window.updateSkillsSelectedCount = updateSkillsSelectedCount; } catch(e) { /* ignore */ }
    // safe no-argument helper to refresh the skills count from console
    try { window.refreshSkillsCount = function(){ try { updateSkillsSelectedCount($('#id_skills_select')); } catch(e) { console.debug('refreshSkillsCount error', e); } }; } catch(e) { /* ignore */ }

    // observe select/options and Select2 container for DOM changes and keep badge realtime
    function setupSkillsRealtimeObserver() {
        try {
            var $sel = $('#id_skills_select');
            if (!$sel || !$sel.length) return;
            var sel = $sel.get(0);
            if (!sel) return;
            // avoid attaching multiple observers
            if (sel._skillsObserverAttached) return;

            function onMutations() { try { updateSkillsSelectedCount($sel); } catch(e){} }

            // observe the native select element for option selection attribute changes and childList changes
            var optObserver = new MutationObserver(function(mutations){ onMutations(); });
            try {
                optObserver.observe(sel, { attributes: true, childList: true, subtree: true, attributeFilter: ['selected'] });
            } catch(e) {
                // some browsers may not allow observing attributeFilter on select; fallback to looser observation
                try { optObserver.observe(sel, { childList: true, subtree: true }); } catch(err) { /* ignore */ }
            }

            // also observe the Select2 container (choices area) if present
            var containerEl = $sel.nextAll('.select2-container, .select2').first().get(0);
            var containerObserver = null;
            if (containerEl) {
                containerObserver = new MutationObserver(function(){ onMutations(); });
                try { containerObserver.observe(containerEl, { childList: true, subtree: true }); } catch(e) { /* ignore */ }
            }

            sel._skillsObserverAttached = true;
            sel._skillsObservers = { opt: optObserver, container: containerObserver };
        } catch(e) { /* ignore */ }
    }

    // Suggest a title when equipment + types are selected and title field is empty.
    function suggestTitleIfEmpty() {
        try {
            var titleInput = document.querySelector('input[name="title"]');
            if (!titleInput) return;
            var cur = (titleInput.value || '').toString().trim();
            if (cur.length) return; // user already typed something

            var eqSelect = $('select[data-ajax-url*="/api/search/equipment"]');
            var eqData = eqSelect.length ? getSelectData(eqSelect)[0] : null;
            var eqLabel = eqData ? (eqData.text || eqData.equipment_id || '') : '';

            var typesSel = $('select[name="workorder_types"]');
            var selTypes = typesSel.length ? getSelectData(typesSel) : [];
            var typeLabels = selTypes.map(function(t){ return t.text || masterWorkTypeLabels[String(t.id)] || ''; }).filter(Boolean);

            if ((eqLabel || typeLabels.length)) {
                var parts = [];
                if (typeLabels.length) parts.push(typeLabels.join('+'));
                if (eqLabel) parts.push(eqLabel);
                var suggestion = parts.join(' - ');
                // show as placeholder-only suggestion (do not change value)
                titleInput.setAttribute('placeholder', suggestion + ' (แตะเพื่อแก้ไข)');
            }
    } catch (e) { /* suppressed suggestTitleIfEmpty error */ }
    }

    // Helper that returns an array of {id, text} for select2-enabled selects or native selects
    function getSelectData($sel) {
        try {
            if (!$sel || !$sel.length) return [];
            // if select2 initialized on this element, use its data
            if (typeof $sel.select2 === 'function' && $sel.hasClass('select2-hidden-accessible')) {
                try { return $sel.select2('data') || []; } catch(e) { /* fallthrough */ }
            }
            // native select: return selected options
            var out = [];
            $sel.find('option:selected').each(function(){ out.push({ id: this.value, text: (this.text || '').trim() }); });
            return out;
        } catch (e) { return []; }
    }

    function handleEquipmentSelectionData(data) {
        try {
            var requires_pm = data && (data.requires_pm === true || data.requires_pm === 'true' || data.requires_pm === 1 || data.requires_pm === '1');
            var requires_cal = data && (data.requires_cal === true || data.requires_cal === 'true' || data.requires_cal === 1 || data.requires_cal === '1');
            var typesSelect = $('select[name="workorder_types"]');
            if (typesSelect.length) {
                var toSelect = [];
                if (requires_pm && masterWorkTypeMap['maintenance']) toSelect.push(String(masterWorkTypeMap['maintenance']));
                if (requires_cal && masterWorkTypeMap['calibration']) toSelect.push(String(masterWorkTypeMap['calibration']));
                if (toSelect.length) {
                    typesSelect.val(toSelect).trigger('change');
                    try {
                        var labels = toSelect.map(function(id){ return masterWorkTypeLabels[String(id)] || id; });
                        if (labels.length) {
                            var msg = 'ระบบเลือกประเภทงานให้อัตโนมัติ: ' + labels.join(', ');
                            showToast('ประเภทงานถูกเลือก', msg, 6000);
                        }
                    } catch (e) { }
                }
            }
    } catch (e) { /* suppressed handleEquipmentSelectionData error */ }
    }

    function setupRealtimeValidation(form) {
        if (!form) return;
        const inputs = Array.from(form.querySelectorAll('input, textarea, select'));

        function getInvalidFeedback(el) {
            if (!el) return null;
            const parent = el.closest('.form-group') || el.parentElement;
            if (!parent) return null;
            return parent.querySelector('.invalid-feedback');
        }

        function validateEl(el) {
            const val = (el.value || '').toString().trim();
            const minlenAttr = el.getAttribute('minlength');
            const minlen = minlenAttr ? parseInt(minlenAttr, 10) : null;
            const fb = getInvalidFeedback(el);

            // empty
            if (!val) {
                el.classList.remove('is-valid');
                el.classList.remove('is-invalid');
                if (fb) fb.classList.add('d-none');
                return;
            }

            if (minlen && val.length < minlen) {
                el.classList.remove('is-valid');
                el.classList.add('is-invalid');
                if (fb) {
                    fb.textContent = 'กรุณากรอกอย่างน้อย ' + minlen + ' ตัวอักษร';
                    fb.classList.remove('d-none');
                }
                return;
            }

            // numeric checks
            if (el.type === 'number') {
                const n = Number(val);
                if (Number.isNaN(n)) {
                    el.classList.remove('is-valid');
                    el.classList.add('is-invalid');
                    if (fb) { fb.textContent = 'ต้องเป็นตัวเลข'; fb.classList.remove('d-none'); }
                    return;
                }
            }

            // date checks (basic YYYY-MM-DD format check by attempting to construct a Date)
            if (el.type === 'date') {
                const d = new Date(val);
                if (isNaN(d.getTime())) {
                    el.classList.remove('is-valid');
                    el.classList.add('is-invalid');
                    if (fb) { fb.textContent = 'รูปแบบวันที่ไม่ถูกต้อง'; fb.classList.remove('d-none'); }
                    return;
                }
            }

            el.classList.remove('is-invalid');
            el.classList.add('is-valid');
            if (fb) fb.classList.add('d-none');
        }

        // ensure every input has an invalid-feedback element for consistent messaging
        inputs.forEach(function(el) {
            const parent = el.closest('.form-group') || el.parentElement;
            if (parent && !parent.querySelector('.invalid-feedback')) {
                const fb = document.createElement('div');
                fb.className = 'invalid-feedback d-none';
                parent.appendChild(fb);
            }
        });

        inputs.forEach(function(el) {
            const fb = getInvalidFeedback(el);
            if ((el.value || '').toString().trim() !== '') {
                if (!el.classList.contains('is-invalid')) {
                    el.classList.add('is-valid');
                    if (fb) fb.classList.add('d-none');
                }
            }
            el.addEventListener('input', function() { validateEl(el); });
            el.addEventListener('change', function() { validateEl(el); });
        });

        // specific: debounce and check uniqueness for equipment_id (configurable via form dataset)
        const eqInput = form.querySelector('input[name="equipment_id"]');
        if (eqInput) {
            let timer = null;
            const endpoint = form.dataset.checkUrl || '/api/check_equipment_id';
            const excludeId = form.dataset.exclude || '';
            function getCsrfToken() {
                // read CSRF token from cookie (Django default)
                const name = 'csrftoken=';
                const cookies = document.cookie.split(';');
                for (let i=0;i<cookies.length;i++){
                    let c = cookies[i].trim();
                    if (c.indexOf(name) === 0) return decodeURIComponent(c.substring(name.length));
                }
                // fallback: from DOM (input[name=csrfmiddlewaretoken])
                const csrfInput = form.querySelector('input[name="csrfmiddlewaretoken"]');
                return csrfInput ? csrfInput.value : '';
            }

            function showSpinner(nextToEl) {
                let s = nextToEl.parentElement.querySelector('.checking-spinner');
                if (!s) {
                    s = document.createElement('span');
                    s.className = 'checking-spinner ms-2';
                    s.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
                    nextToEl.parentElement.appendChild(s);
                }
                s.style.display = '';
                return s;
            }

            function hideSpinner(sp) { if (sp) sp.style.display = 'none'; }

            function checkUnique() {
                const val = (eqInput.value || '').toString().trim();
                const fb = getInvalidFeedback(eqInput);
                if (!val) return;
                if (val.length < 13) return; // other validator covers this
                const sp = showSpinner(eqInput);
                const body = { equipment_id: val };
                if (excludeId) body.exclude = excludeId;
                fetch(endpoint, {
                    method: 'POST',
                    credentials: 'same-origin',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken()
                    },
                    body: JSON.stringify(body)
                }).then(function(resp){
                    return resp.json();
                }).then(function(json){
                    hideSpinner(sp);
                    if (!json) return;
                    if (json.exists) {
                        eqInput.classList.remove('is-valid');
                        eqInput.classList.add('is-invalid');
                        if (fb) { fb.textContent = json.message || 'รหัสนี้มีอยู่แล้ว'; fb.classList.remove('d-none'); }
                    } else {
                        eqInput.classList.remove('is-invalid');
                        eqInput.classList.add('is-valid');
                        if (fb) fb.classList.add('d-none');
                    }
                }).catch(function(){
                    hideSpinner(sp);
                });
            }
            eqInput.addEventListener('input', function(){
                if (timer) clearTimeout(timer);
                timer = setTimeout(checkUnique, 450);
            });
        }
    }

    function setupEquipmentButtons() {
        const equipmentInput = document.getElementById('equipment_id_input') || document.querySelector('input[name="equipment_id"]');
        const useBtn = document.getElementById('use_suggested_btn');
        const copyBtn = document.getElementById('copy_id_btn');
        const suggestedEl = document.getElementById('suggested_code');

        if (useBtn && equipmentInput && suggestedEl) {
            useBtn.addEventListener('click', function() {
                equipmentInput.value = suggestedEl.textContent.trim();
                equipmentInput.dispatchEvent(new Event('input'));
                equipmentInput.focus();
            });
        }

        if (copyBtn && equipmentInput) {
            copyBtn.addEventListener('click', function() {
                const val = equipmentInput.value || '';
                if (!val) return;
                navigator.clipboard && navigator.clipboard.writeText ? navigator.clipboard.writeText(val) : (function(){
                    const ta = document.createElement('textarea'); ta.value = val; document.body.appendChild(ta); ta.select(); document.execCommand('copy'); ta.remove();
                })();
                copyBtn.classList.add('btn-success');
                setTimeout(()=>copyBtn.classList.remove('btn-success'), 900);
            });
        }
    }

    function setupDeleteButtons() {
        document.addEventListener('click', function(e) {
            const btn = e.target.closest && e.target.closest('.delete-btn');
            if (!btn) return;
            e.preventDefault();
            // prefer numeric PK stored in data-eqid, but fall back to equipment code in data-eq-qr
            const eqid = btn.getAttribute('data-eqid') || btn.getAttribute('data-eq-qr') || '';
            const eqname = btn.getAttribute('data-eqname') || '';
            const message = `ยืนยันการลบข้อมูล ${eqid} , ${eqname} ?`;
            if (confirm(message)) {
                // follow the link
                window.location.href = btn.href;
            }
        });
    }

    function setupConfirmButtons() {
        document.addEventListener('click', function(e) {
            const el = e.target.closest && e.target.closest('.confirm-btn');
            if (!el) return;
            const msg = el.getAttribute('data-confirm') || 'ยืนยันการกระทำ?';
            if (!confirm(msg)) {
                e.preventDefault();
            } // if confirmed, allow default action (link will follow)
        });
    }

    // init on DOM ready
    $(function(){
    // preload master items mapping for workorder_type (code -> id)
        $.getJSON('/api/master/items', { category: 'workorder_type' }).done(function(resp){
            if (resp && resp.results) {
                resp.results.forEach(function(it){
                    if (it.code) masterWorkTypeMap[it.code] = it.id;
                    if (it.id) masterWorkTypeLabels[String(it.id)] = it.label || it.code || String(it.id);
                });
            }
        }).fail(function(){ /* ignore */ }).always(function(){
            initSelect2();
            // initial suggestion
            setTimeout(suggestTitleIfEmpty, 250);
            // ensure skills selected count initialized after select2 init
            try { setTimeout(function(){ updateSkillsSelectedCount($('#id_skills_select')); setupSkillsRealtimeObserver(); }, 350); } catch(e){}

            // Persistent polling fallback: update badge every 250ms to guarantee realtime UX
            try {
                if (!window._skillsPollInterval) {
                    window._skillsPollInterval = setInterval(function(){
                        try { updateSkillsSelectedCount($('#id_skills_select')); } catch(e) { /* ignore */ }
                    }, 250);
                }
            } catch(e) { /* ignore */ }
        });

        // Delegated handlers to keep skills count realtime even if Select2 re-inits or events are missed
        // handle select2 selection/unselection events bubbling via document
        $(document).on('select2:select select2:unselect change.select2', 'select#id_skills_select', function(e){
            try { updateSkillsSelectedCount($('#id_skills_select')); setupSkillsRealtimeObserver(); } catch(err) { /* ignore */ }
        });
        // handle native change on the select as well
        $(document).on('change', 'select#id_skills_select', function(e){
            try { updateSkillsSelectedCount($('#id_skills_select')); setupSkillsRealtimeObserver(); } catch(err) { /* ignore */ }
        });

        // click on per-technician skills count button -> show modal with skills
        $(document).on('click', '.skills-count', function(e){
            try {
                var btn = e.currentTarget;
                // find nearest skills-labels sibling
                var row = btn.closest && btn.closest('.list-group-item');
                var labelsEl = row ? row.querySelector('.skills-labels') : null;
                var bodyHtml = '';
                if (labelsEl) {
                    bodyHtml = '<p>' + (labelsEl.textContent || labelsEl.innerText || '').trim() + '</p>';
                } else {
                    bodyHtml = '<p class="text-muted">ไม่พบข้อมูลทักษะ</p>';
                }
                var modalEl = document.getElementById('skills-modal');
                if (!modalEl) return;
                var modalBody = modalEl.querySelector('.modal-body');
                if (modalBody) modalBody.innerHTML = bodyHtml;
                if (window.bootstrap && typeof bootstrap.Modal === 'function') {
                    var inst = bootstrap.Modal.getOrCreateInstance(modalEl);
                    inst.show();
                } else if (typeof $ === 'function' && $.fn && typeof $.fn.modal === 'function') {
                    $('#skills-modal').modal('show');
                } else {
                    // fallback: set display
                    modalEl.classList.add('show'); modalEl.style.display = 'block';
                }
            } catch(err) { console.debug('skills-count click handler error', err); }
        });

        // Polling fallback: short-lived interval to catch any missed updates (cleans up itself)
        (function(){
            var last = null;
            var tries = 0;
            var poll = setInterval(function(){
                try {
                    var $s = $('#id_skills_select');
                    if (!$s || !$s.length) { if (++tries > 10) clearInterval(poll); return; }
                    var cur = ($s.find('option:selected').length || 0) + '|' + (($s.select2 && $s.hasClass('select2-hidden-accessible')) ? ($s.select2('data')||[]).length : 0);
                    if (cur !== last) {
                        last = cur;
                        updateSkillsSelectedCount($s);
                    }
                } catch(e) { /* ignore polling errors */ }
                if (++tries > 40) clearInterval(poll); // stop after ~4s
            }, 100);
        })();
        // prefer explicit forms that provide a check URL (covers add/edit)
        const checkForms = Array.from(document.querySelectorAll('form[data-check-url]'));
        if (checkForms.length) {
            checkForms.forEach(function(f){ setupRealtimeValidation(f); });
        } else {
            // backwards-compatible fallback
            setupRealtimeValidation(document.querySelector('form[action="add_equipment"]') || document.querySelector('form'));
        }
        setupEquipmentButtons();
        setupDeleteButtons();
        setupConfirmButtons();
        // update suggestion when equipment or workorder_types change
        $(document).on('change', 'select[data-ajax-url*="/api/search/equipment"]', function(){ setTimeout(suggestTitleIfEmpty, 50); });
        $(document).on('change', 'select[name="workorder_types"]', function(){ setTimeout(suggestTitleIfEmpty, 50); });
        // show accept-suggestion button when placeholder suggests something
        function updateAcceptSuggestionButton() {
            try {
                var btn = document.getElementById('accept_title_suggestion_btn');
                var titleInput = document.querySelector('input[name="title"]');
                if (!btn || !titleInput) return;
                var placeholder = titleInput.getAttribute('placeholder') || '';
                if (placeholder && placeholder.length > 0 && (titleInput.value || '').toString().trim().length === 0) {
                    btn.style.display = '';
                } else {
                    btn.style.display = 'none';
                }
            } catch(e){ }
        }
        // periodically update button visibility after suggestion changes
        $(document).on('change select2:select', 'select[name="workorder_types"], select[data-ajax-url*="/api/search/equipment"]', function(){ setTimeout(updateAcceptSuggestionButton, 120); });
        // when clicking the accept button, copy placeholder into title input as value
        $(document).on('click', '#accept_title_suggestion_btn', function(){
            try {
                var titleInput = document.querySelector('input[name="title"]');
                if (!titleInput) return;
                var ph = titleInput.getAttribute('placeholder') || '';
                if (ph) {
                    // remove the helper suffix if present
                    ph = ph.replace(/ \(แตะเพื่อแก้ไข\)$/, '');
                    titleInput.value = ph;
                    titleInput.dispatchEvent(new Event('input'));
                    // mark hidden input so server knows suggestion was accepted
                    var hid = document.getElementById('accepted_title_suggestion');
                    if (hid) hid.value = '1';
                    // hide button after apply
                    document.getElementById('accept_title_suggestion_btn').style.display = 'none';
                    // show a small toast to confirm
                    showToast('ยอมรับคำแนะนำ', 'หัวข้อถูกตั้งตามคำแนะนำแล้ว', 3500);
                }
            } catch(e){}
        });
        // hide suggestion button when user starts typing
        $(document).on('input', 'input[name="title"]', function(){
            var btn = document.getElementById('accept_title_suggestion_btn'); if (btn) btn.style.display = 'none';
        });
    });

    // Modal fallback: if the types select would overlap on medium screens, allow opening a chooser modal
    function ensureTypesModal() {
        if (document.getElementById('workorder-types-modal')) return;
        var modalHtml = '\n<div class="modal fade" id="workorder-types-modal" tabindex="-1" aria-hidden="true">\n  <div class="modal-dialog modal-lg">\n    <div class="modal-content">\n      <div class="modal-header">\n        <h5 class="modal-title">เลือกประเภทงาน</h5>\n        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>\n      </div>\n      <div class="modal-body">\n        <div id="workorder-types-modal-body">Loading...</div>\n      </div>\n      <div class="modal-footer">\n        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">ยกเลิก</button>\n        <button type="button" class="btn btn-primary" id="workorder-types-modal-apply">นำไปใช้</button>\n      </div>\n    </div>\n  </div>\n</div>\n';
        document.body.insertAdjacentHTML('beforeend', modalHtml);

        // build modal content from existing select options when opened
        $(document).on('show.bs.modal', '#workorder-types-modal', function(){
            var dst = document.getElementById('workorder-types-modal-body');
            var sel = document.querySelector('select[name="workorder_types"]');
            if (!sel) { dst.innerHTML = '<p>ไม่พบรายการประเภทงาน</p>'; return; }
            var html = '<div class="list-group">';
            Array.from(sel.options).forEach(function(opt){
                var id = opt.value || '';
                var label = (opt.text || '').trim();
                var checked = opt.selected ? ' checked' : '';
                html += '<label class="list-group-item"><input type="checkbox" class="workorder-type-checkbox me-2" value="'+id+'"'+checked+'> '+label+'</label>';
            });
            html += '</div>';
            dst.innerHTML = html;
        });

        // apply selected checkboxes back to the original select
        $(document).on('click', '#workorder-types-modal-apply', function(){
            var sel = document.querySelector('select[name="workorder_types"]');
            if (!sel) return;
            var checks = Array.from(document.querySelectorAll('.workorder-type-checkbox'));
            var values = checks.filter(function(c){ return c.checked; }).map(function(c){ return c.value; });
            // set values on select (works for native multiple select)
            $(sel).val(values).trigger('change');
            var m = bootstrap.Modal.getInstance(document.getElementById('workorder-types-modal'));
            if (m) m.hide();
        });
    }

    // add a small chooser button next to the types select on medium widths
    function addTypesChooserButton() {
        var sel = document.querySelector('select[name="workorder_types"]');
        if (!sel) return;
        // avoid duplicate button
        if (document.getElementById('open-types-chooser')) return;
        var btn = document.createElement('button');
        btn.type = 'button';
        btn.id = 'open-types-chooser';
        btn.className = 'btn btn-outline-secondary btn-sm ms-2';
        btn.textContent = 'เลือกแบบเต็มหน้าจอ';
        // insert after select
        sel.parentNode.insertBefore(btn, sel.nextSibling);
        ensureTypesModal();
        btn.addEventListener('click', function(){
            var md = new bootstrap.Modal(document.getElementById('workorder-types-modal'));
            md.show();
        });
    }

    // Add chooser button responsively: only show when viewport is between 768px and 1399px
    function updateChooserVisibility() {
        var w = window.innerWidth || document.documentElement.clientWidth;
        var btn = document.getElementById('open-types-chooser');
        if (w >= 768 && w < 1400) {
            if (!btn) addTypesChooserButton();
        } else {
            if (btn) btn.remove();
        }
    }

    window.addEventListener('resize', function(){ setTimeout(updateChooserVisibility, 120); });
    $(function(){ setTimeout(updateChooserVisibility, 250); });
    // initialize inline equipment search
    setTimeout(initInlineEquipmentSearch, 350);

    // Equipment modal search logic
    function initEquipmentModal() {
        var openBtn = document.getElementById('open-equipment-search');
        var modalEl = document.getElementById('equipment-search-modal');
    // initialization: no console logging in production
        if (!openBtn) return;
        if (!modalEl) return; // nothing to do if modal element missing
        var modal = null;
        try {
            if (!modalEl.querySelector('.modal-dialog')) {
                // modal DOM seems malformed; silently continue and allow fallback injection
            }
            if (window.bootstrap && typeof bootstrap.Modal === 'function') {
                // prefer safe getOrCreateInstance when available to avoid internal initialization issues
                if (typeof bootstrap.Modal.getOrCreateInstance === 'function') {
                    try {
                        modal = bootstrap.Modal.getOrCreateInstance(modalEl);
                    } catch (err) {
                        // bootstrap.getOrCreateInstance error suppressed; try constructor fallback
                        try { modal = new bootstrap.Modal(modalEl, {}); } catch(e) { /* suppressed */ }
                    }
                } else {
                    modal = new bootstrap.Modal(modalEl, {});
                }
            }
    } catch(e) { /* suppressed bootstrap modal init error */ modal = null; }

        // helper to set visibility and ARIA/inert consistently
        function setModalVisibility(el, visible) {
            try {
                if (!el) return;
                if (visible) {
                    el.classList.add('show');
                    el.style.display = 'block';
                    try { el.setAttribute('aria-hidden', 'false'); } catch(e){}
                    try { el.inert = false; } catch(e){}
                    if (!document.querySelector('.modal-backdrop')) {
                        var bd = document.createElement('div'); bd.className = 'modal-backdrop fade show'; document.body.appendChild(bd);
                    }
                } else {
                    // move focus away if needed
                    try {
                        var active = document.activeElement;
                        if (active && el.contains(active)) {
                            try { if (openBtn && typeof openBtn.focus === 'function') { openBtn.focus(); } else if (document.body && typeof document.body.focus === 'function') { document.body.focus(); } } catch(e) { try { active.blur(); } catch(err){} }
                        }
                    } catch(e){}
                    try { el.setAttribute('aria-hidden', 'true'); } catch(e){}
                    try { el.inert = true; } catch(e){}
                    el.classList.remove('show');
                    el.style.display = 'none';
                    var bd = document.querySelector('.modal-backdrop'); if (bd) bd.remove();
                }
            } catch(e) { /* suppressed setModalVisibility error */ }
        }

        function showModal() {
            try {
                if (modal && typeof modal.show === 'function') {
                    modal.show();
                } else if (typeof $ === 'function' && $.fn && typeof $.fn.modal === 'function') {
                    $('#equipment-search-modal').modal('show');
                } else {
                    // fallback: use helper to consistently set visibility/ARIA
                    try { setModalVisibility(modalEl, true); } catch(e) { /* suppressed manual show fallback error */ }
                }
                // ensure consumers relying on shown.bs.modal still work
                    setTimeout(function(){ try { modalEl.dispatchEvent(new Event('shown.bs.modal')); } catch(e){} }, 120);
            } catch(e) { /* suppressed showModal fallback error */ }
        }
        function hideModal() {
            try {
                if (modal && typeof modal.hide === 'function') return modal.hide();
                if (typeof $ === 'function' && $.fn && typeof $.fn.modal === 'function') return $('#equipment-search-modal').modal('hide');
                try {
                    // use helper to hide consistently
                    setModalVisibility(modalEl, false);
                } catch(e) { /* suppressed manual hide fallback error */ }
            } catch(e) { /* suppressed hideModal fallback error */ }
        }
        var input = document.getElementById('equipment-search-input');
        var results = document.getElementById('equipment-search-results');

        function renderResults(items) {
            if (!results) return;
            if (!items || !items.length) {
                results.innerHTML = '<div class="text-muted">ไม่พบผลลัพธ์</div><div class="mt-2"><a class="btn btn-sm btn-outline-secondary" href="/equipment_list" target="_blank">ดูรายการอุปกรณ์ทั้งหมด</a></div>';
                return;
            }
            var html = '<div class="list-group">';
            items.forEach(function(it){
                // api returns {id, text, requires_pm, requires_cal}
                var title = it.text || ( (it.equipment_id?it.equipment_id+' - ':'') + (it.equipment_name_TH||it.equipment_name_EN||it.label||'') );
                var flags = [];
                if (it.requires_pm) flags.push('PM');
                if (it.requires_cal) flags.push('CAL');
                var sub = flags.length ? '<span class="badge bg-info ms-1">'+flags.join(',')+'</span>' : '';
                // make whole item clickable and include an explicit select button
                // include equipment code (equipment_id) when available as data-eq-qr, fall back to id
                html += '<button type="button" class="list-group-item list-group-item-action d-flex justify-content-between align-items-start select-equipment-row" data-eqid="'+(it.id||'')+'" data-eq-qr="'+(it.equipment_id||it.id||'')+'" data-eqtext="'+escapeHtml(title)+'" data-requires_pm="'+(it.requires_pm?1:0)+'" data-requires_cal="'+(it.requires_cal?1:0)+'">\n  <div>\n    <div class="fw-bold">'+escapeHtml(title)+'</div>\n    <div class="text-muted small">'+(it.location||'')+' '+(it.note||'')+' '+sub+'</div>\n  </div>\n  <div class="text-nowrap">\n    <span class="me-2 text-muted small">'+(flags.length?flags.join(', '):'')+'</span>\n    <span><span class="btn btn-sm btn-primary select-equipment-btn" role="button">เลือก</span></span>\n  </div>\n</button>';
            });
            html += '</div>';
            results.innerHTML = html;
        }

        function doSearch(q) {
            results.innerHTML = '<div class="text-muted">กำลังค้นหา…</div>';
            // gather filter checkbox values from modal
            var pm = document.getElementById('filter_requires_pm_modal');
            var cal = document.getElementById('filter_requires_cal_modal');
            var params = { q: q };
            if (pm && pm.checked) params.requires_pm = 1;
            if (cal && cal.checked) params.requires_cal = 1;
            $.getJSON('/api/search/equipment', params).done(function(resp){
                var items = resp && resp.results ? resp.results : [];
                cacheLastEquipmentResults(items);
                renderResults(items);
            }).fail(function(){ results.innerHTML = '<div class="text-danger">เกิดข้อผิดพลาดขณะค้นหา</div>'; });
        }

        openBtn.addEventListener('click', function(){
            showModal();
            // clear previous
            if (input) { input.value = ''; }
            results.innerHTML = '<div class="text-muted">กำลังโหลดรายการอุปกรณ์…</div>';
            setTimeout(function(){ if (input) input.focus(); }, 200);
        });

        // ensure ARIA and focus state is correct when modal is shown/hidden
        modalEl.addEventListener('show.bs.modal', function(){
            try {
                // mark visible for assistive tech
                modalEl.setAttribute('aria-hidden', 'false');
                try { modalEl.inert = false; } catch(e) {}
                // focus the search input when modal opens
                setTimeout(function(){ if (input && typeof input.focus === 'function') try { input.focus(); } catch(e){} }, 80);
            } catch(e) { /* suppressed modal show handler error */ }
        });

        // when the modal is fully shown, load equipment list (empty q -> server returns first page)
        modalEl.addEventListener('shown.bs.modal', function(){
            try {
                doSearch((input && input.value) ? input.value : '');
            } catch(e) { /* suppressed error loading equipment list on modal show */ }
        });

        modalEl.addEventListener('hidden.bs.modal', function(){
            try {
                // if some element inside modal still has focus, move focus back to the opener or body
                var active = document.activeElement;
                if (active && modalEl.contains(active)) {
                    try { if (openBtn && typeof openBtn.focus === 'function') { openBtn.focus(); } else if (document.body && typeof document.body.focus === 'function') { document.body.focus(); } } catch(e) { try { active.blur(); } catch(err){} }
                }
                // mark hidden for AT and prevent focus
                try { modalEl.setAttribute('aria-hidden', 'true'); } catch(e){}
                try { modalEl.inert = true; } catch(e){}
                // ensure backdrop removed
                var bd = document.querySelector('.modal-backdrop'); if (bd) bd.remove();
            } catch(e) { /* suppressed modal hidden handler error */ }
        });

        // when user types into the display field, open modal and forward the query
        var displayField = document.getElementById('equipment_display');
        function forwardQuery(q) { if (!input) return; input.value = q || ''; doSearch(q || ''); }
        if (displayField) {
            displayField.addEventListener('input', function(e){
                var q = (displayField.value || '').toString().trim();
                // open modal and forward the query
                if (!document.getElementById('equipment-search-modal').classList.contains('show')) {
                    try { showModal(); } catch(e){ window.openEquipmentSearch && window.openEquipmentSearch(); }
                }
                setTimeout(function(){ forwardQuery(q); }, 220);
            });

            // allow clicking/typing on the display field to open modal and forward typed keys
            displayField.addEventListener('click', function(){ try { showModal(); } catch(e){ window.openEquipmentSearch && window.openEquipmentSearch(); } });
            displayField.addEventListener('keydown', function(e){
                // open modal on any printable key and forward that key
                var isPrintable = e.key && e.key.length === 1;
                if (isPrintable) {
                    try { showModal(); } catch(e){ window.openEquipmentSearch && window.openEquipmentSearch(); }
                    setTimeout(function(){
                        if (input) {
                            input.value = e.key;
                            input.focus();
                        }
                    }, 220);
                    e.preventDefault();
                }
                // allow Enter to open search
                if (e.key === 'Enter') { try { showModal(); } catch(e){ window.openEquipmentSearch && window.openEquipmentSearch(); } setTimeout(function(){ if (input) input.focus(); }, 220); e.preventDefault(); }
            });
        }

        if (input) {
            input.addEventListener('keydown', function(e){ if (e.key === 'Enter') { e.preventDefault(); doSearch(input.value); } });
        }

        // handle clicks inside the results container for selection
        if (results) {
            results.addEventListener('click', function(e){
                var row = e.target.closest && e.target.closest('.select-equipment-row');
                var btn = e.target.closest && e.target.closest('.select-equipment-btn');
                var el = row || btn;
                if (!el) return;
                // prefer attributes on row, fall back to button wrapper attributes
                // prefer numeric PK in data-eqid, but fall back to equipment code in data-eq-qr
                var id = el.getAttribute('data-eqid') || (btn && btn.getAttribute('data-eqid')) || el.getAttribute('data-eq-qr') || (btn && btn.getAttribute('data-eq-qr')) || '';
                var text = el.getAttribute('data-eqtext') || (btn && btn.getAttribute('data-eqtext')) || '';
                // data- attributes on row are strings '1'/'0'
                var requires_pm = (el.getAttribute('data-requires_pm') === '1') || (btn && btn.getAttribute('data-requires_pm') === '1');
                var requires_cal = (el.getAttribute('data-requires_cal') === '1') || (btn && btn.getAttribute('data-requires_cal') === '1');
                if (!id) return;
                var hid = document.getElementById('equipment_input');
                var disp = document.getElementById('equipment_display');
                if (hid) hid.value = id;
                if (disp) disp.value = text;
                handleEquipmentSelectionData({ requires_pm: requires_pm, requires_cal: requires_cal });
                hideModal();
            });
        }
    }

    // Inline search (shows results under equipment_display input)
    function initInlineEquipmentSearch() {
        var disp = document.getElementById('equipment_display');
        var inline = document.getElementById('equipment-inline-results');
        if (!disp || !inline) return;

        function showInline(items) {
            if (!items || !items.length) { inline.style.display = 'none'; inline.innerHTML = ''; return; }
            var html = '';
            items.forEach(function(it){
                var text = it.text || (it.equipment_id + ' - ' + (it.equipment_name_TH||it.equipment_name_EN||it.label||''));
                // include equipment code as data-eq-qr (fallback to id if code not present)
                html += '<button type="button" class="list-group-item list-group-item-action inline-select" data-eqid="'+(it.id||'')+'" data-eq-qr="'+(it.equipment_id||it.id||'')+'" data-eqtext="'+escapeHtml(text)+'" data-requires_pm="'+(it.requires_pm?1:0)+'" data-requires_cal="'+(it.requires_cal?1:0)+'">'+escapeHtml(text)+'</button>';
            });
            inline.innerHTML = html;
            inline.style.display = '';
        }

        var timer = null;
        disp.addEventListener('input', function(){
            var q = (disp.value || '').toString().trim();
            if (timer) clearTimeout(timer);
            timer = setTimeout(function(){
                if (!q) { inline.style.display = 'none'; return; }
                // call API with inline filter checkboxes
                var pmInline = document.getElementById('filter_requires_pm_inline');
                var calInline = document.getElementById('filter_requires_cal_inline');
                var params = { q: q };
                if (pmInline && pmInline.checked) params.requires_pm = 1;
                if (calInline && calInline.checked) params.requires_cal = 1;
                $.getJSON('/api/search/equipment', params).done(function(resp){ var items = resp && resp.results ? resp.results : []; showInline(items); cacheLastEquipmentResults(items); }).fail(function(){ inline.style.display='none'; });
            }, 250);
        });

        // click on inline item
        inline.addEventListener('click', function(e){
            var btn = e.target.closest && e.target.closest('.inline-select');
            if (!btn) return;
            // prefer numeric PK, fall back to equipment code
            var id = btn.getAttribute('data-eqid') || btn.getAttribute('data-eq-qr') || '';
            var text = btn.getAttribute('data-eqtext') || btn.textContent || '';
            var requires_pm = btn.getAttribute('data-requires_pm') === '1';
            var requires_cal = btn.getAttribute('data-requires_cal') === '1';
            var hid = document.getElementById('equipment_input');
            if (hid) hid.value = id;
            disp.value = text;
            inline.style.display = 'none';
            var selected = findCachedEquipmentById(id);
            if (selected) renderEquipmentDetails(selected);
            handleEquipmentSelectionData({ requires_pm: requires_pm, requires_cal: requires_cal });
        });

        // hide when clicking outside
        document.addEventListener('click', function(e){ if (!disp.contains(e.target) && !inline.contains(e.target)) { inline.style.display='none'; } });
    }

    // small cache of last equipment results returned from API (array)
    var _lastEquipmentResults = [];
    function cacheLastEquipmentResults(items) { try { _lastEquipmentResults = items || []; } catch(e){} }
    function findCachedEquipmentById(id) {
        try {
            if (!id) return null;
            return _lastEquipmentResults.find(function(it){
                // match either the numeric PK (id) or the equipment code (equipment_id)
                return String(it.id) === String(id) || String(it.equipment_id || '') === String(id);
            }) || null;
        } catch(e){ return null; }
    }

    function renderEquipmentDetails(item) {
        try {
            if (!item) { document.getElementById('equipment-details').style.display = 'none'; return; }
            var panel = document.getElementById('equipment-details');
            var title = document.getElementById('eq-details-title');
            var body = document.getElementById('eq-details-body');
            title.textContent = (item.equipment_id || item.text || '') + ' ' + (item.equipment_name_TH || item.equipment_name_EN || '');
            var html = '<div><strong>แบรนด์:</strong> ' + (item.brand||'') + '</div>';
            html += '<div><strong>รุ่น:</strong> ' + (item.model||'') + '</div>';
            html += '<div><strong>หน่วยงาน:</strong> ' + ((item.user_unit||'') + ' / ' + (item.user_section||'') + ' / ' + (item.user_department||'')) + '</div>';
            if (item.pm_due) html += '<div><strong>PM due:</strong> ' + item.pm_due + '</div>';
            if (item.cal_due) html += '<div><strong>CAL due:</strong> ' + item.cal_due + '</div>';
            if (item.note) html += '<div class="text-muted small">' + escapeHtml(item.note) + '</div>';
            body.innerHTML = html;
            panel.style.display = '';
    } catch(e) { /* suppressed renderEquipmentDetails error */ }
    }

    // simple html escaper for attributes
    function escapeHtml(s) { return (''+s).replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }

    // initialize equipment modal when DOM ready
    $(function(){ setTimeout(initEquipmentModal, 300); });

    // fallback global opener for the equipment modal (safe to call from inline onclick)
    window.openEquipmentSearch = function(){
        try {
            var modalEl = document.getElementById('equipment-search-modal');
            var input = document.getElementById('equipment-search-input');
            // openEquipmentSearch called (no instrumentation log)
            if (!modalEl) {
                // Modal markup missing in DOM; create a minimal modal and append to body so opener works
                try {
                    var modalHtml = '\n<div class="modal fade" id="equipment-search-modal" tabindex="-1" aria-hidden="true">\n  <div class="modal-dialog modal-xl modal-fullscreen-md-down">\n    <div class="modal-content">\n      <div class="modal-header">\n        <h5 class="modal-title">ค้นหาอุปกรณ์</h5>\n        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>\n      </div>\n      <div class="modal-body">\n        <div class="mb-3">\n          <input type="search" id="equipment-search-input" class="form-control" placeholder="ค้นหาด้วยรหัสหรือชื่อ (พิมพ์แล้วกด Enter)">\n        </div>\n        <div class="mb-3">\n          <div class="form-check form-check-inline">\n            <input class="form-check-input" type="checkbox" id="filter_requires_pm_modal" value="1">\n            <label class="form-check-label" for="filter_requires_pm_modal">Requires PM</label>\n          </div>\n          <div class="form-check form-check-inline">\n            <input class="form-check-input" type="checkbox" id="filter_requires_cal_modal" value="1">\n            <label class="form-check-label" for="filter_requires_cal_modal">Requires CAL</label>\n          </div>\n        </div>\n        <div id="equipment-search-results" style="min-height:200px;">กรุณาค้นหา</div>\n      </div>\n      <div class="modal-footer">\n        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">ปิด</button>\n      </div>\n    </div>\n  </div>\n</div>\n';
                    document.body.insertAdjacentHTML('beforeend', modalHtml);
                    modalEl = document.getElementById('equipment-search-modal');
                    input = document.getElementById('equipment-search-input');
                    // try to re-bind modal handlers (initEquipmentModal is in scope)
                    try { if (typeof initEquipmentModal === 'function') initEquipmentModal(); } catch(e) { /* suppressed initEquipmentModal reinit error */ }
                    // injected equipment-search-modal into DOM
                } catch(e) {
                    /* suppressed failed to inject equipment-search-modal */
                }
            }
            if (!modalEl) return;
            // Try Bootstrap 5 safe API
            if (window.bootstrap && typeof bootstrap.Modal === 'function' && typeof bootstrap.Modal.getOrCreateInstance === 'function') {
                try {
                    var inst = bootstrap.Modal.getOrCreateInstance(modalEl);
                    if (inst && typeof inst.show === 'function') { inst.show(); }
                } catch(e) { /* suppressed bootstrap.getOrCreateInstance/show error */ }
            } else if (typeof $ === 'function' && $.fn && typeof $.fn.modal === 'function') {
                try { $('#equipment-search-modal').modal('show'); } catch(e) { /* suppressed jquery modal show error */ }
            } else {
                // manual fallback: add show class and backdrop
                try {
                    modalEl.classList.add('show'); modalEl.style.display = 'block';
                    try { modalEl.setAttribute('aria-hidden', 'false'); } catch(e){}
                    try { modalEl.inert = false; } catch(e){}
                    // add backdrop if none
                    if (!document.querySelector('.modal-backdrop')) {
                        var bd = document.createElement('div'); bd.className = 'modal-backdrop fade show'; document.body.appendChild(bd);
                    }
                } catch(e) { console.debug('manual modal show error', e); }
            }
            setTimeout(function(){ try { if (input) input.focus(); } catch(e){}; try { modalEl.dispatchEvent(new Event('shown.bs.modal')); } catch(e){} }, 200);
        } catch(e) { /* suppressed openEquipmentSearch fallback error */ }
    };

    // synchronize inline and modal filter checkboxes (inline <-> modal)
    function syncEquipmentFilterCheckboxes() {
        try {
            var inlinePm = document.getElementById('filter_requires_pm_inline');
            var inlineCal = document.getElementById('filter_requires_cal_inline');
            var modalPm = document.getElementById('filter_requires_pm_modal');
            var modalCal = document.getElementById('filter_requires_cal_modal');
            function bind(a,b){ if(!a||!b) return; a.addEventListener('change', function(){ try{ b.checked = a.checked; }catch(e){} }); }
            bind(inlinePm, modalPm); bind(modalPm, inlinePm);
            bind(inlineCal, modalCal); bind(modalCal, inlineCal);
            var modalEl = document.getElementById('equipment-search-modal');
            if (modalEl) modalEl.addEventListener('show.bs.modal', function(){
                try {
                    if (inlinePm && modalPm) modalPm.checked = inlinePm.checked;
                    if (inlineCal && modalCal) modalCal.checked = inlineCal.checked;
                } catch(e) { /* ignore */ }
            });
        } catch(e) { /* suppressed */ }
    }
    $(function(){ syncEquipmentFilterCheckboxes(); });

    // Engineer/BME confirm button behavior
    function setupEngineerConfirm() {
        try {
            var btn = document.getElementById('engineer_confirm_btn');
            var unbtn = document.getElementById('engineer_unconfirm_btn');
            var hid = document.getElementById('engineer_confirmed');
            if (!btn || !hid) return;
            btn.addEventListener('click', function(){
                hid.value = '1';
                btn.classList.remove('btn-outline-primary');
                btn.classList.add('btn-primary');
                btn.textContent = 'ยืนยันแล้ว';
                if (unbtn) unbtn.style.display = '';
                showToast('ยืนยันโดยวิศวกร/BME', 'เอกสารนี้ถูกยืนยันโดยวิศวกรหรือทีม BME แล้ว', 4000);
            });
            if (unbtn) {
                unbtn.addEventListener('click', function(){
                    hid.value = '0';
                    btn.classList.remove('btn-primary');
                    btn.classList.add('btn-outline-primary');
                    btn.textContent = 'ยืนยันโดยวิศวกร/BME';
                    unbtn.style.display = 'none';
                    showToast('ยกเลิกการยืนยัน', 'การยืนยันโดยวิศวกร/BME ถูกยกเลิกแล้ว', 3000);
                });
            }
        } catch(e) { console.debug('setupEngineerConfirm error', e); }
    }
    $(function(){ setupEngineerConfirm(); });
    // Create service request button on left column
    function setupCreateServiceRequest() {
        try {
            var btn = document.getElementById('create_service_request_btn');
            var hid = document.getElementById('create_service_request');
            if (!btn || !hid) return;
            btn.addEventListener('click', function(){
                try { hid.value = '1'; }
                catch(e){}
                // submit the nearest form
                var f = document.querySelector('form.needs-validation');
                if (f) f.submit();
            });
        } catch(e){ console.debug('setupCreateServiceRequest error', e); }
    }
    $(function(){ setupCreateServiceRequest(); });
})(window, document);
