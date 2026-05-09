# Codex generated code begins
"""Tkinter user interface for TaskBoard."""

# pylint: disable=line-too-long,too-many-ancestors,too-many-instance-attributes
# pylint: disable=too-many-locals,too-many-statements

import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from src.entities.project import Project
from src.entities.task import Task
from src.entities.user import User
from src.repositories.database import initialize_database
from src.repositories.label_repository import LabelRepository
from src.repositories.project_repository import ProjectRepository
from src.repositories.task_repository import TaskRepository
from src.repositories.user_repository import UserRepository
from src.services.auth_service import (
    AuthService,
    AuthenticationError,
    RegistrationError,
    RegistrationInput,
)
from src.services.label_service import (
    LabelAssignmentError,
    LabelCreationError,
    LabelService,
)
from src.services.project_service import (
    ProjectCreationContext,
    ProjectCreationError,
    ProjectDeleteError,
    ProjectSearchError,
    ProjectService,
    ProjectTaskError,
)
from src.services.session_service import SessionService
from src.services.task_service import (
    TaskCompleteError,
    TaskCreationContext,
    TaskCreationError,
    TaskDeleteError,
    TaskEditError,
    TaskSearchError,
    TaskService,
)
from src.services.user_profile_service import UserProfileError, UserProfileService


class TaskBoardApp(tk.Tk):
    """Main Tkinter application window."""

    def __init__(self) -> None:
        """Create repositories, services, and the first view."""
        super().__init__()
        self.title("TaskBoard")
        self.geometry("1050x680")
        self.minsize(900, 560)

        initialize_database()
        self.user_repository = UserRepository()
        self.task_repository = TaskRepository()
        self.project_repository = ProjectRepository()
        self.label_repository = LabelRepository()
        self.auth_service = AuthService(self.user_repository)
        self.session_service = SessionService()
        self.task_service = TaskService(self.task_repository)
        self.project_service = ProjectService(self.project_repository, self.task_repository)
        self.label_service = LabelService(self.label_repository, self.task_repository)
        self.user_profile_service = UserProfileService(
            self.user_repository,
            self.project_repository,
            self.task_repository,
        )

        self.current_frame: ttk.Frame | None = None
        self.show_sign_in()

    def replace_frame(self, frame: ttk.Frame) -> None:
        """Replace current visible view."""
        if self.current_frame is not None:
            self.current_frame.destroy()
        self.current_frame = frame
        self.current_frame.pack(fill=tk.BOTH, expand=True)

    def current_user(self) -> User | None:
        """Return signed-in user."""
        return self.session_service.get_current_user()

    def show_sign_in(self) -> None:
        """Show sign-in view."""
        self.replace_frame(SignInView(self))

    def show_sign_up(self) -> None:
        """Show sign-up view."""
        self.replace_frame(SignUpView(self))

    def show_home(self) -> None:
        """Show signed-in home view."""
        self.replace_frame(HomeView(self))

    def show_user_profile(self, user_id: int | None) -> None:
        """Show user profile view."""
        self.replace_frame(UserProfileView(self, user_id))

    def show_project(self, project_id: int | None) -> None:
        """Show project details view."""
        self.replace_frame(ProjectView(self, project_id))

    def show_task(self, task_id: int | None) -> None:
        """Show task details view."""
        self.replace_frame(TaskView(self, task_id))

    def sign_out(self) -> None:
        """Sign out and return to sign-in view."""
        self.session_service.sign_out()
        self.show_sign_in()


class SignInView(ttk.Frame):
    """Sign-in screen."""

    def __init__(self, app: TaskBoardApp) -> None:
        """Create sign-in form."""
        super().__init__(app, padding=32)
        self.app = app
        self.email_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self._build()

    def _build(self) -> None:
        """Build widgets."""
        panel = ttk.Frame(self)
        panel.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        ttk.Label(panel, text="TaskBoard", font=("TkDefaultFont", 24, "bold")).grid(
            row=0,
            column=0,
            columnspan=2,
            pady=(0, 24),
        )
        ttk.Label(panel, text="Email").grid(row=1, column=0, sticky=tk.W, pady=4)
        ttk.Entry(panel, textvariable=self.email_var, width=36).grid(row=1, column=1, pady=4)
        ttk.Label(panel, text="Password").grid(row=2, column=0, sticky=tk.W, pady=4)
        ttk.Entry(panel, textvariable=self.password_var, show="*", width=36).grid(
            row=2,
            column=1,
            pady=4,
        )
        ttk.Button(panel, text="Sign in", command=self._sign_in).grid(
            row=3,
            column=0,
            columnspan=2,
            sticky=tk.EW,
            pady=(16, 6),
        )
        ttk.Button(panel, text="Create account", command=self.app.show_sign_up).grid(
            row=4,
            column=0,
            columnspan=2,
            sticky=tk.EW,
        )

    def _sign_in(self) -> None:
        """Authenticate user."""
        try:
            user = self.app.auth_service.sign_in(
                self.email_var.get(),
                self.password_var.get(),
            )
        except AuthenticationError as error:
            messagebox.showerror("Sign in failed", str(error))
            return

        self.app.session_service.sign_in_user(user)
        self.app.show_home()


class SignUpView(ttk.Frame):
    """Account registration screen."""

    def __init__(self, app: TaskBoardApp) -> None:
        """Create registration form."""
        super().__init__(app, padding=32)
        self.app = app
        self.first_name_var = tk.StringVar()
        self.last_name_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.confirm_password_var = tk.StringVar()
        self._build()

    def _build(self) -> None:
        """Build widgets."""
        panel = ttk.Frame(self)
        panel.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        ttk.Label(panel, text="Create Account", font=("TkDefaultFont", 20, "bold")).grid(
            row=0,
            column=0,
            columnspan=2,
            pady=(0, 20),
        )

        fields = (
            ("First name", self.first_name_var, False),
            ("Last name", self.last_name_var, False),
            ("Email", self.email_var, False),
            ("Password", self.password_var, True),
            ("Confirm password", self.confirm_password_var, True),
        )
        for row, (label, variable, secret) in enumerate(fields, start=1):
            ttk.Label(panel, text=label).grid(row=row, column=0, sticky=tk.W, pady=4)
            ttk.Entry(panel, textvariable=variable, show="*" if secret else "", width=36).grid(
                row=row,
                column=1,
                pady=4,
            )

        ttk.Button(panel, text="Register", command=self._register_account).grid(
            row=6,
            column=0,
            columnspan=2,
            sticky=tk.EW,
            pady=(16, 6),
        )
        ttk.Button(panel, text="Back to sign in", command=self.app.show_sign_in).grid(
            row=7,
            column=0,
            columnspan=2,
            sticky=tk.EW,
        )

    def _register_account(self) -> None:
        """Register user and return to sign-in view."""
        registration = RegistrationInput(
            first_name=self.first_name_var.get(),
            last_name=self.last_name_var.get(),
            email=self.email_var.get(),
            password=self.password_var.get(),
            confirm_password=self.confirm_password_var.get(),
        )
        try:
            self.app.auth_service.register(registration)
        except RegistrationError as error:
            messagebox.showerror("Registration failed", str(error))
            return

        messagebox.showinfo("Account created", "You can now sign in.")
        self.app.show_sign_in()


class HomeView(ttk.Frame):
    """Home screen with tasks, projects, search, and actions."""

    def __init__(self, app: TaskBoardApp) -> None:
        """Create home screen."""
        super().__init__(app, padding=16)
        self.app = app
        self.task_rows: dict[str, int] = {}
        self.project_rows: dict[str, int] = {}
        self.search_var = tk.StringVar()
        self._build()
        self._load_data()

    def _build(self) -> None:
        """Build widgets."""
        user = self.app.current_user()
        header = ttk.Frame(self)
        header.pack(fill=tk.X, pady=(0, 12))
        signed_in = f"{user.first_name} {user.last_name}" if user is not None else ""
        ttk.Label(header, text=f"Signed in as {signed_in}", font=("TkDefaultFont", 12, "bold")).pack(
            side=tk.LEFT
        )
        ttk.Button(header, text="My page", command=self._open_my_page).pack(side=tk.RIGHT, padx=4)
        ttk.Button(header, text="Sign out", command=self.app.sign_out).pack(side=tk.RIGHT, padx=4)

        search_row = ttk.Frame(self)
        search_row.pack(fill=tk.X, pady=(0, 12))
        ttk.Entry(search_row, textvariable=self.search_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(search_row, text="Search", command=self._search).pack(side=tk.LEFT, padx=4)
        ttk.Button(search_row, text="Clear", command=self._clear_search).pack(side=tk.LEFT)

        content = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        content.pack(fill=tk.BOTH, expand=True)

        tasks_panel = ttk.LabelFrame(content, text="Tasks", padding=8)
        projects_panel = ttk.LabelFrame(content, text="Projects", padding=8)
        content.add(tasks_panel, weight=3)
        content.add(projects_panel, weight=2)

        task_columns = ("title", "priority", "labels", "due", "status")
        self.tasks_tree = ttk.Treeview(
            tasks_panel,
            columns=task_columns,
            show="headings",
            selectmode="browse",
        )
        for column, label in zip(
            task_columns,
            ("Title", "Priority", "Labels", "Due date", "Status"),
        ):
            self.tasks_tree.heading(column, text=label)
        self.tasks_tree.column("title", width=260)
        self.tasks_tree.column("priority", width=90)
        self.tasks_tree.column("labels", width=160)
        self.tasks_tree.column("due", width=100)
        self.tasks_tree.column("status", width=90)
        self.tasks_tree.pack(fill=tk.BOTH, expand=True)
        self.tasks_tree.bind("<Double-1>", lambda _event: self._open_selected_task())

        task_buttons = ttk.Frame(tasks_panel)
        task_buttons.pack(fill=tk.X, pady=(8, 0))
        for text, command in (
            ("New", self._create_task),
            ("Open", self._open_selected_task),
            ("Edit", self._edit_selected_task),
            ("Complete", self._complete_selected_task),
            ("Delete", self._delete_selected_task),
            ("New label", self._create_label),
            ("Add label", self._add_label_to_task),
        ):
            ttk.Button(task_buttons, text=text, command=command).pack(side=tk.LEFT, padx=2)

        project_columns = ("name", "priority", "due")
        self.projects_tree = ttk.Treeview(
            projects_panel,
            columns=project_columns,
            show="headings",
            selectmode="browse",
        )
        for column, label in zip(project_columns, ("Name", "Priority", "Due date")):
            self.projects_tree.heading(column, text=label)
        self.projects_tree.column("name", width=220)
        self.projects_tree.column("priority", width=90)
        self.projects_tree.column("due", width=100)
        self.projects_tree.pack(fill=tk.BOTH, expand=True)
        self.projects_tree.bind("<Double-1>", lambda _event: self._open_selected_project())

        project_buttons = ttk.Frame(projects_panel)
        project_buttons.pack(fill=tk.X, pady=(8, 0))
        ttk.Button(project_buttons, text="New project", command=self._create_project).pack(
            side=tk.LEFT,
            padx=2,
        )
        ttk.Button(project_buttons, text="Open", command=self._open_selected_project).pack(
            side=tk.LEFT,
            padx=2,
        )

    def _load_data(self) -> None:
        """Load active tasks and projects."""
        user = self.app.current_user()
        if user is None:
            return
        tasks = self.app.task_repository.list_tasks_for_user(user.id)
        projects = self.app.project_service.list_projects_for_user(user.id)
        self._set_tasks(tasks)
        self._set_projects(projects)

    def _set_tasks(self, tasks: list[Task]) -> None:
        """Replace task rows."""
        self.tasks_tree.delete(*self.tasks_tree.get_children())
        self.task_rows = {}
        for task in tasks:
            row_id = self.tasks_tree.insert(
                "",
                tk.END,
                values=(
                    task.title,
                    task.priority,
                    self._format_task_labels(task),
                    task.due_date or "",
                    "completed" if task.is_completed else "active",
                ),
            )
            if task.id is not None:
                self.task_rows[row_id] = task.id

    def _set_projects(self, projects: list[Project]) -> None:
        """Replace project rows."""
        self.projects_tree.delete(*self.projects_tree.get_children())
        self.project_rows = {}
        for project in projects:
            row_id = self.projects_tree.insert(
                "",
                tk.END,
                values=(project.name, project.priority, project.due_date or ""),
            )
            if project.id is not None:
                self.project_rows[row_id] = project.id

    def _selected_task_id(self) -> int | None:
        """Return selected task id."""
        selected = self.tasks_tree.selection()
        if not selected:
            return None
        return self.task_rows.get(selected[0])

    def _selected_project_id(self) -> int | None:
        """Return selected project id."""
        selected = self.projects_tree.selection()
        if not selected:
            return None
        return self.project_rows.get(selected[0])

    def _open_my_page(self) -> None:
        """Open signed-in user's page."""
        user = self.app.current_user()
        self.app.show_user_profile(user.id if user is not None else None)

    def _search(self) -> None:
        """Search visible tasks and projects."""
        user = self.app.current_user()
        try:
            tasks = self.app.task_service.search_tasks(
                user.id if user is not None else None,
                self.search_var.get(),
            )
            projects = self.app.project_service.search_projects(
                user.id if user is not None else None,
                self.search_var.get(),
            )
        except (TaskSearchError, ProjectSearchError) as error:
            messagebox.showerror("Search failed", str(error))
            return
        self._set_tasks(tasks)
        self._set_projects(projects)

    def _clear_search(self) -> None:
        """Clear search and reload home lists."""
        self.search_var.set("")
        self._load_data()

    def _create_task(self) -> None:
        """Open task creation dialog."""
        dialog = TaskDialog(self.app, "Create Task")
        if dialog.result is None:
            return
        user = self.app.current_user()
        try:
            self.app.task_service.create_task(
                dialog.result["title"],
                dialog.result["description"],
                TaskCreationContext(
                    creator_user_id=user.id if user is not None else None,
                    priority=dialog.result["priority"],
                    due_date=dialog.result["due_date"],
                ),
            )
        except TaskCreationError as error:
            messagebox.showerror("Task creation failed", str(error))
            return
        self._load_data()

    def _edit_selected_task(self) -> None:
        """Edit selected task."""
        task = self._load_selected_task()
        if task is None:
            return
        dialog = TaskDialog(self.app, "Edit Task", task)
        if dialog.result is None:
            return
        user = self.app.current_user()
        try:
            self.app.task_service.edit_task(
                task.id,
                user.id if user is not None else None,
                dialog.result["title"],
                dialog.result["description"],
            )
        except TaskEditError as error:
            messagebox.showerror("Task edit failed", str(error))
            return
        self._load_data()

    def _complete_selected_task(self) -> None:
        """Complete selected task."""
        task_id = self._selected_task_id()
        user = self.app.current_user()
        if task_id is None:
            messagebox.showinfo("Select task", "Select a task first.")
            return
        try:
            self.app.task_service.complete_task(task_id, user.id if user is not None else None)
        except TaskCompleteError as error:
            messagebox.showerror("Task completion failed", str(error))
            return
        self._load_data()

    def _delete_selected_task(self) -> None:
        """Delete selected task."""
        task_id = self._selected_task_id()
        user = self.app.current_user()
        if task_id is None:
            messagebox.showinfo("Select task", "Select a task first.")
            return
        if not messagebox.askyesno("Delete task", "Delete selected task?"):
            return
        try:
            self.app.task_service.delete_task(task_id, user.id if user is not None else None)
        except TaskDeleteError as error:
            messagebox.showerror("Task deletion failed", str(error))
            return
        self._load_data()

    def _create_project(self) -> None:
        """Open project creation dialog."""
        users = self.app.user_repository.list_users()
        dialog = ProjectDialog(self.app, users)
        if dialog.result is None:
            return
        user = self.app.current_user()
        try:
            self.app.project_service.create_project(
                dialog.result["name"],
                ProjectCreationContext(
                    owner_user_id=user.id if user is not None else None,
                    member_user_ids=dialog.result["member_ids"],
                    priority=dialog.result["priority"],
                    due_date=dialog.result["due_date"],
                ),
            )
        except ProjectCreationError as error:
            messagebox.showerror("Project creation failed", str(error))
            return
        self._load_data()

    def _open_selected_task(self) -> None:
        """Open selected task details."""
        task_id = self._selected_task_id()
        if task_id is None:
            messagebox.showinfo("Select task", "Select a task first.")
            return
        self.app.show_task(task_id)

    def _open_selected_project(self) -> None:
        """Open selected project details."""
        project_id = self._selected_project_id()
        if project_id is None:
            messagebox.showinfo("Select project", "Select a project first.")
            return
        self.app.show_project(project_id)

    def _load_selected_task(self) -> Task | None:
        """Return selected task object."""
        task_id = self._selected_task_id()
        user = self.app.current_user()
        if task_id is None or user is None:
            messagebox.showinfo("Select task", "Select a task first.")
            return None
        task = self.app.task_repository.find_task_for_user(task_id, user.id)
        if task is None:
            messagebox.showerror("Task not found", "Task was not found.")
        return task

    def _create_label(self) -> None:
        """Create a label."""
        name = simpledialog.askstring("Create label", "Label name:", parent=self.app)
        if name is None:
            return
        try:
            self.app.label_service.create_label(name)
        except LabelCreationError as error:
            messagebox.showerror("Label creation failed", str(error))

    def _add_label_to_task(self) -> None:
        """Attach label to selected task."""
        task_id = self._selected_task_id()
        user = self.app.current_user()
        if task_id is None:
            messagebox.showinfo("Select task", "Select a task first.")
            return
        labels = self.app.label_service.list_labels()
        dialog = LabelSelectionDialog(self.app, labels)
        if dialog.label_id is None:
            return
        try:
            self.app.label_service.add_label_to_task(
                task_id,
                dialog.label_id,
                user.id if user is not None else None,
            )
        except LabelAssignmentError as error:
            messagebox.showerror("Label assignment failed", str(error))
            return
        self._load_data()

    def _format_task_labels(self, task: Task) -> str:
        """Return comma-separated labels for a task."""
        return ", ".join(
            label.name for label in self.app.label_service.list_labels_for_task(task.id)
        )


class TaskView(ttk.Frame):
    """Task details screen."""

    def __init__(self, app: TaskBoardApp, task_id: int | None) -> None:
        """Create task details screen."""
        super().__init__(app, padding=16)
        self.app = app
        self.task_id = task_id
        self._build()

    def _build(self) -> None:
        """Build widgets."""
        user = self.app.current_user()
        task = None
        if self.task_id is not None and user is not None:
            task = self.app.task_repository.find_task_for_user(self.task_id, user.id)
        if task is None:
            ttk.Label(self, text="Task was not found.").pack(anchor=tk.W)
            ttk.Button(self, text="Back", command=self.app.show_home).pack(anchor=tk.W, pady=8)
            return

        ttk.Button(self, text="Back", command=self.app.show_home).pack(anchor=tk.W)
        ttk.Label(self, text=task.title, font=("TkDefaultFont", 20, "bold")).pack(
            anchor=tk.W,
            pady=(16, 8),
        )
        labels = ", ".join(label.name for label in self.app.label_service.list_labels_for_task(task.id))
        details = (
            f"Description: {task.description}\n"
            f"Priority: {task.priority}\n"
            f"Due date: {task.due_date or 'none'}\n"
            f"Status: {'completed' if task.is_completed else 'active'}\n"
            f"Labels: {labels or 'none'}"
        )
        ttk.Label(self, text=details, justify=tk.LEFT).pack(anchor=tk.W)
        ttk.Button(
            self,
            text="View creator",
            command=lambda: self.app.show_user_profile(task.created_by_user_id),
        ).pack(anchor=tk.W, pady=12)


class ProjectView(ttk.Frame):
    """Project details screen."""

    def __init__(self, app: TaskBoardApp, project_id: int | None) -> None:
        """Create project details screen."""
        super().__init__(app, padding=16)
        self.app = app
        self.project_id = project_id
        self.task_rows: dict[str, int] = {}
        self._build()

    def _build(self) -> None:
        """Build widgets."""
        ttk.Button(self, text="Back", command=self.app.show_home).pack(anchor=tk.W)
        user = self.app.current_user()
        try:
            details = self.app.project_service.get_project_details(
                self.project_id,
                user.id if user is not None else None,
            )
        except ProjectTaskError as error:
            ttk.Label(self, text=str(error)).pack(anchor=tk.W, pady=16)
            return

        header = ttk.Frame(self)
        header.pack(fill=tk.X, pady=(16, 8))
        ttk.Label(
            header,
            text=details.project.name,
            font=("TkDefaultFont", 20, "bold"),
        ).pack(side=tk.LEFT)
        ttk.Button(
            header,
            text="View creator",
            command=lambda: self.app.show_user_profile(details.project.created_by_user_id),
        ).pack(side=tk.RIGHT)
        ttk.Button(
            header,
            text="Delete project",
            command=lambda: self._delete_project(details.project),
        ).pack(side=tk.RIGHT, padx=4)

        ttk.Label(
            self,
            text=f"Priority: {details.project.priority}    Due date: {details.project.due_date or 'none'}",
        ).pack(anchor=tk.W)

        members = ", ".join(f"{member.first_name} {member.last_name}" for member in details.members)
        ttk.Label(self, text=f"Members: {members or 'none'}").pack(anchor=tk.W, pady=(4, 16))

        buttons = ttk.Frame(self)
        buttons.pack(fill=tk.X, pady=(0, 8))
        ttk.Button(
            buttons,
            text="Create task in project",
            command=lambda: self._create_project_task(details),
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            buttons,
            text="Add existing task",
            command=lambda: self._add_existing_task(details),
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(buttons, text="Open task", command=self._open_selected_task).pack(
            side=tk.LEFT,
            padx=2,
        )

        columns = ("title", "priority", "labels", "due", "status")
        self.tasks_tree = ttk.Treeview(self, columns=columns, show="headings", selectmode="browse")
        for column, label in zip(columns, ("Title", "Priority", "Labels", "Due date", "Status")):
            self.tasks_tree.heading(column, text=label)
        self.tasks_tree.pack(fill=tk.BOTH, expand=True)
        self.tasks_tree.bind("<Double-1>", lambda _event: self._open_selected_task())
        self.task_rows = {}
        for task in details.tasks:
            row_id = self.tasks_tree.insert(
                "",
                tk.END,
                values=(
                    task.title,
                    task.priority,
                    self._format_task_labels(task),
                    task.due_date or "",
                    "completed" if task.is_completed else "active",
                ),
            )
            if task.id is not None:
                self.task_rows[row_id] = task.id

    def _format_task_labels(self, task: Task) -> str:
        """Return comma-separated labels for a project task."""
        return ", ".join(
            label.name for label in self.app.label_service.list_labels_for_task(task.id)
        )

    def _selected_task_id(self) -> int | None:
        """Return selected project task id."""
        selected = self.tasks_tree.selection()
        if not selected:
            return None
        return self.task_rows.get(selected[0])

    def _open_selected_task(self) -> None:
        """Open selected project task."""
        task_id = self._selected_task_id()
        if task_id is None:
            messagebox.showinfo("Select task", "Select a task first.")
            return
        self.app.show_task(task_id)

    def _create_project_task(self, details) -> None:
        """Create a new task inside project."""
        dialog = TaskDialog(self.app, "Create Project Task")
        if dialog.result is None:
            return
        user = self.app.current_user()
        member_ids = [member.id for member in details.members if member.id is not None]
        try:
            self.app.task_service.create_task(
                dialog.result["title"],
                dialog.result["description"],
                TaskCreationContext(
                    creator_user_id=user.id if user is not None else None,
                    project_id=details.project.id,
                    participant_user_ids=member_ids,
                    priority=dialog.result["priority"],
                    due_date=dialog.result["due_date"],
                ),
            )
        except TaskCreationError as error:
            messagebox.showerror("Task creation failed", str(error))
            return
        self.app.show_project(details.project.id)

    def _add_existing_task(self, details) -> None:
        """Add an existing user task to project."""
        user = self.app.current_user()
        tasks = self.app.project_service.list_available_tasks_for_project(
            details.project.id,
            user.id if user is not None else None,
        )
        dialog = TaskSelectionDialog(self.app, tasks)
        if dialog.task_id is None:
            return
        try:
            self.app.project_service.add_existing_task_to_project(
                details.project.id,
                dialog.task_id,
                user.id if user is not None else None,
            )
        except ProjectTaskError as error:
            messagebox.showerror("Project update failed", str(error))
            return
        self.app.show_project(details.project.id)

    def _delete_project(self, project: Project) -> None:
        """Delete project."""
        user = self.app.current_user()
        if not messagebox.askyesno("Delete project", f"Delete project '{project.name}'?"):
            return
        try:
            self.app.project_service.delete_project(project.id, user.id if user is not None else None)
        except ProjectDeleteError as error:
            messagebox.showerror("Project deletion failed", str(error))
            return
        self.app.show_home()


class UserProfileView(ttk.Frame):
    """User profile screen."""

    def __init__(self, app: TaskBoardApp, user_id: int | None) -> None:
        """Create user profile screen."""
        super().__init__(app, padding=16)
        self.app = app
        self.user_id = user_id
        self._build()

    def _build(self) -> None:
        """Build widgets."""
        ttk.Button(self, text="Back", command=self.app.show_home).pack(anchor=tk.W)
        try:
            profile = self.app.user_profile_service.get_profile(self.user_id)
        except UserProfileError as error:
            ttk.Label(self, text=str(error)).pack(anchor=tk.W, pady=16)
            return

        ttk.Label(
            self,
            text=f"{profile.user.first_name} {profile.user.last_name}",
            font=("TkDefaultFont", 20, "bold"),
        ).pack(anchor=tk.W, pady=(16, 4))
        ttk.Label(self, text=profile.user.email).pack(anchor=tk.W, pady=(0, 16))

        content = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        content.pack(fill=tk.BOTH, expand=True)
        projects_panel = ttk.LabelFrame(content, text="Project memberships", padding=8)
        tasks_panel = ttk.LabelFrame(content, text="Task participation", padding=8)
        content.add(projects_panel, weight=1)
        content.add(tasks_panel, weight=1)

        projects = tk.Listbox(projects_panel)
        projects.pack(fill=tk.BOTH, expand=True)
        for project in profile.projects:
            projects.insert(tk.END, f"{project.name} [{project.priority}]")

        tasks = tk.Listbox(tasks_panel)
        tasks.pack(fill=tk.BOTH, expand=True)
        for task in profile.tasks:
            status = "completed" if task.is_completed else "active"
            tasks.insert(tk.END, f"{task.title} [{status}, {task.priority}]")


class TaskDialog(simpledialog.Dialog):
    """Dialog for task creation and editing."""

    def __init__(self, parent: tk.Tk, title: str, task: Task | None = None) -> None:
        """Create task dialog."""
        self.task = task
        self.title_var = tk.StringVar(value=task.title if task is not None else "")
        self.description_var = tk.StringVar(value=task.description if task is not None else "")
        self.priority_var = tk.StringVar(value=task.priority if task is not None else "medium")
        self.due_date_var = tk.StringVar(value=task.due_date if task and task.due_date else "")
        self.result = None
        super().__init__(parent, title)

    def body(self, master: ttk.Frame):
        """Build dialog body."""
        ttk.Label(master, text="Title").grid(row=0, column=0, sticky=tk.W, pady=4)
        title_entry = ttk.Entry(master, textvariable=self.title_var, width=40)
        title_entry.grid(row=0, column=1, pady=4)
        ttk.Label(master, text="Description").grid(row=1, column=0, sticky=tk.W, pady=4)
        ttk.Entry(master, textvariable=self.description_var, width=40).grid(row=1, column=1, pady=4)
        ttk.Label(master, text="Priority").grid(row=2, column=0, sticky=tk.W, pady=4)
        ttk.Combobox(
            master,
            textvariable=self.priority_var,
            values=("low", "medium", "high"),
            state="readonly",
        ).grid(row=2, column=1, sticky=tk.EW, pady=4)
        ttk.Label(master, text="Due date").grid(row=3, column=0, sticky=tk.W, pady=4)
        ttk.Entry(master, textvariable=self.due_date_var, width=40).grid(row=3, column=1, pady=4)
        return title_entry

    def apply(self) -> None:
        """Store dialog result."""
        self.result = {
            "title": self.title_var.get(),
            "description": self.description_var.get(),
            "priority": self.priority_var.get(),
            "due_date": self.due_date_var.get(),
        }


class ProjectDialog(simpledialog.Dialog):
    """Dialog for project creation."""

    def __init__(self, parent: tk.Tk, users: list[User]) -> None:
        """Create project dialog."""
        self.users = users
        self.name_var = tk.StringVar()
        self.priority_var = tk.StringVar(value="medium")
        self.due_date_var = tk.StringVar()
        self.members_listbox = None
        self.result = None
        super().__init__(parent, "Create Project")

    def body(self, master: ttk.Frame):
        """Build dialog body."""
        ttk.Label(master, text="Name").grid(row=0, column=0, sticky=tk.W, pady=4)
        name_entry = ttk.Entry(master, textvariable=self.name_var, width=40)
        name_entry.grid(row=0, column=1, pady=4)
        ttk.Label(master, text="Priority").grid(row=1, column=0, sticky=tk.W, pady=4)
        ttk.Combobox(
            master,
            textvariable=self.priority_var,
            values=("low", "medium", "high"),
            state="readonly",
        ).grid(row=1, column=1, sticky=tk.EW, pady=4)
        ttk.Label(master, text="Due date").grid(row=2, column=0, sticky=tk.W, pady=4)
        ttk.Entry(master, textvariable=self.due_date_var, width=40).grid(row=2, column=1, pady=4)
        ttk.Label(master, text="Members").grid(row=3, column=0, sticky=tk.NW, pady=4)
        self.members_listbox = tk.Listbox(master, selectmode=tk.MULTIPLE, height=8, width=40)
        self.members_listbox.grid(row=3, column=1, pady=4)
        for user in self.users:
            self.members_listbox.insert(tk.END, f"{user.first_name} {user.last_name} ({user.email})")
        return name_entry

    def apply(self) -> None:
        """Store dialog result."""
        selected_indices = self.members_listbox.curselection() if self.members_listbox else []
        selected_users = [self.users[index] for index in selected_indices]
        self.result = {
            "name": self.name_var.get(),
            "priority": self.priority_var.get(),
            "due_date": self.due_date_var.get(),
            "member_ids": [user.id for user in selected_users if user.id is not None],
        }


class LabelSelectionDialog(simpledialog.Dialog):
    """Dialog for selecting a label."""

    def __init__(self, parent: tk.Tk, labels) -> None:
        """Create label selection dialog."""
        self.labels = labels
        self.label_listbox = None
        self.label_id = None
        super().__init__(parent, "Select Label")

    def body(self, master: ttk.Frame):
        """Build dialog body."""
        self.label_listbox = tk.Listbox(master, height=8, width=32)
        self.label_listbox.pack(fill=tk.BOTH, expand=True)
        for label in self.labels:
            self.label_listbox.insert(tk.END, label.name)
        return self.label_listbox

    def apply(self) -> None:
        """Store selected label id."""
        if self.label_listbox is None:
            return
        selected = self.label_listbox.curselection()
        if selected:
            self.label_id = self.labels[selected[0]].id


class TaskSelectionDialog(simpledialog.Dialog):
    """Dialog for selecting a task."""

    def __init__(self, parent: tk.Tk, tasks: list[Task]) -> None:
        """Create task selection dialog."""
        self.tasks = tasks
        self.task_listbox = None
        self.task_id = None
        super().__init__(parent, "Select Task")

    def body(self, master: ttk.Frame):
        """Build dialog body."""
        self.task_listbox = tk.Listbox(master, height=8, width=48)
        self.task_listbox.pack(fill=tk.BOTH, expand=True)
        for task in self.tasks:
            self.task_listbox.insert(tk.END, task.title)
        return self.task_listbox

    def apply(self) -> None:
        """Store selected task id."""
        if self.task_listbox is None:
            return
        selected = self.task_listbox.curselection()
        if selected:
            self.task_id = self.tasks[selected[0]].id


def main() -> None:
    """Start the Tkinter application."""
    app = TaskBoardApp()
    app.mainloop()


if __name__ == "__main__":
    main()
# Codex generated code ends
