from nicegui import ui
import httpx

API_BASE = 'http://localhost:8080/api/todos'
todos = []

ui.label('📋 Todo List').classes('text-2xl font-bold')
ui.button('➕ Add Todo', on_click=lambda: open_create_dialog()).props('color=primary')

def fetch_todos():
    try:
        response = httpx.get(API_BASE)
        response.raise_for_status()
        todos.clear()
        todos.extend(response.json())
        render_table()
    except Exception as e:
        ui.notify(f'Failed to fetch todos: {e}')

def show_detail(todo_id):
    dialog = ui.dialog()
    with dialog:
        with ui.card():
            ui.label(f'Todo Detail - ID: {todo_id}').classes('text-xl font-bold')

            try:
                res = httpx.get(f'{API_BASE}/{todo_id}')
                res.raise_for_status()
                todo = res.json()
            except Exception as e:
                ui.label(f'❌ Failed to load todo: {e}')
                return

            ui.label(f'📝 Title: {todo["title"]}')
            ui.label(f'🧾 Description: {todo["description"] or "-"}')
            ui.label(f'📅 Due Date: {todo.get("dueDate") or "-"}')
            ui.label(f'📌 Status: {todo["status"]}')

            ui.button('UPDATE', on_click=lambda: open_update_dialog(todo)).props('color=primary')
            ui.button('Change Status', on_click=lambda: open_status_dialog(todo)).props('color=accent')
            ui.button('🗑 DELETE', on_click=lambda: confirm_delete(todo['id'])).props('color=negative')
            ui.button('CLOSE', on_click=dialog.close).props('color=secondary')

    dialog.open()

def open_update_dialog(todo):
    dialog = ui.dialog()
    with dialog:
        with ui.card():
            ui.label('✏️ Update Todo').classes('text-lg font-bold')
            title_input = ui.input(label='Title', value=todo['title'])
            desc_input = ui.textarea(label='Description', value=todo.get('description') or '')
            due_input = ui.input(label='Due Date (YYYY-MM-DD)', value=todo.get('dueDate') or '')

            def save_update():
                try:
                    payload = {
                        'title': title_input.value,
                        'description': desc_input.value or None,
                        'dueDate': due_input.value or None,
                        'status': todo['status']
                    }
                    res = httpx.put(f'{API_BASE}/{todo["id"]}', json=payload)
                    res.raise_for_status()
                    ui.notify('✅ Updated successfully')
                    dialog.close()
                    fetch_todos()
                except Exception as e:
                    ui.notify(f'❌ Failed to update: {e}')

            ui.button('Save', on_click=save_update).props('color=primary')
            ui.button('Cancel', on_click=dialog.close).props('color=secondary')

    dialog.open()

def open_status_dialog(todo):
    dialog = ui.dialog()
    with dialog:
        with ui.card():
            ui.label('🔄 Change Status').classes('text-lg font-bold')
            status_select = ui.select(['PENDING', 'DONE'], value=todo['status'], label='Select Status')

            def save_status():
                try:
                    payload = {
                        'title': todo['title'],
                        'description': todo.get('description'),
                        'dueDate': todo.get('dueDate'),
                        'status': status_select.value
                    }
                    res = httpx.put(f'{API_BASE}/{todo["id"]}', json=payload)
                    res.raise_for_status()
                    ui.notify('✅ Status updated')
                    dialog.close()
                    fetch_todos()
                except Exception as e:
                    ui.notify(f'❌ Failed to update status: {e}')

            ui.button('Save', on_click=save_status).props('color=primary')
            ui.button('Cancel', on_click=dialog.close).props('color=secondary')

    dialog.open()

def confirm_delete(todo_id):
    dialog = ui.dialog()
    with dialog:
        with ui.card():
            ui.label('⚠️ Confirm Deletion').classes('text-lg font-bold')
            ui.label('Are you sure you want to delete this todo?')

            with ui.row():
                def delete_todo():
                    try:
                        res = httpx.delete(f'{API_BASE}/{todo_id}')
                        res.raise_for_status()
                        ui.notify('✅ Todo deleted')
                        dialog.close()
                        fetch_todos()
                    except Exception as e:
                        ui.notify(f'❌ Failed to delete: {e}')
                        dialog.close()

                ui.button('Yes, Delete', on_click=delete_todo).props('color=negative')
                ui.button('Cancel', on_click=dialog.close).props('color=secondary')

    dialog.open()

def open_create_dialog():
    dialog = ui.dialog()
    with dialog:
        with ui.card():
            ui.label('🆕 Add New Todo').classes('text-lg font-bold')
            title_input = ui.input(label='Title')
            desc_input = ui.textarea(label='Description')
            due_input = ui.input(label='Due Date (YYYY-MM-DD)')
            status_select = ui.select(['PENDING', 'DONE'], value='PENDING', label='Status')

            def save_todo():
                try:
                    payload = {
                        'title': title_input.value,
                        'description': desc_input.value or None,
                        'dueDate': due_input.value or None,
                        'status': status_select.value
                    }
                    res = httpx.post(API_BASE, json=payload)
                    res.raise_for_status()
                    ui.notify('✅ Todo created successfully')
                    dialog.close()
                    fetch_todos()
                except Exception as e:
                    ui.notify(f'❌ Failed to create todo: {e}')

            ui.button('Save', on_click=save_todo).props('color=primary')
            ui.button('Cancel', on_click=dialog.close).props('color=secondary')

    dialog.open()

table_area = ui.column().classes('w-full')

def render_table():
    table_area.clear()
    with table_area:
        with ui.row().classes('w-full items-center no-wrap text-bold'):
            ui.label('ID').classes('w-1/12')
            ui.label('Title').classes('w-4/12')
            ui.label('Due Date').classes('w-3/12')
            ui.label('Status').classes('w-2/12')
            ui.label('Action').classes('w-2/12')

        for todo in todos:
            with ui.row().classes('w-full items-center no-wrap'):
                ui.label(str(todo['id'])).classes('w-1/12')
                ui.label(todo['title']).classes('w-4/12')
                ui.label(todo.get('dueDate') or '-').classes('w-3/12')
                ui.label(todo['status']).classes('w-2/12')
                ui.button('View', on_click=lambda t=todo['id']: show_detail(t)).classes('w-2/12')

fetch_todos()
ui.run(port=3030, title='Todo List App')
