"""CLI interface for TODO application"""

from .models import TaskManager, Task


def print_header():
    """Print application header"""
    print("\n" + "=" * 50)
    print("📝 CLI TODO APP")
    print("=" * 50)


def print_menu():
    """Print command menu"""
    print("""
Commands:
  add <title>     - Add new task
  list            - List all tasks
  done <id>       - Mark task as completed
  delete <id>     - Delete a task
  search <query>  - Search tasks
  stats          - Show statistics
  clear          - Clear completed tasks
  help           - Show this menu
  quit           - Exit application
""")


def print_tasks(tasks: list, title: str = "Tasks"):
    """Print task list"""
    if not tasks:
        print(f"\n{title}: No tasks found")
        return
    
    print(f"\n{title} ({len(tasks)}):")
    print("-" * 40)
    for task in tasks:
        print(f"  {task}")
        if task.description:
            print(f"      └─ {task.description[:50]}...")


def format_stats(stats: dict) -> str:
    """Format statistics for display"""
    return f"""
📊 Statistics:
   Total tasks: {stats['total']}
   ✓ Completed: {stats['completed']}
   ○ Pending: {stats['pending']}
   
   By Priority (pending):
   🔴 High: {stats['by_priority']['high']}
   🟡 Medium: {stats['by_priority']['medium']}
   🔵 Low: {stats['by_priority']['low']}
"""


def run():
    """Main application loop"""
    manager = TaskManager()
    
    print_header()
    print_menu()
    
    while True:
        try:
            user_input = input("\n> ").strip()
            
            if not user_input:
                continue
            
            parts = user_input.split(maxsplit=1)
            command = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""
            
            if command in ("quit", "exit", "q"):
                print("\n👋 Goodbye!")
                break
            
            elif command == "help":
                print_menu()
            
            elif command == "add":
                if not args:
                    print("❌ Please provide a task title")
                    continue
                
                # Parse priority if provided
                priority = "medium"
                if args.startswith("["):
                    end = args.find("]")
                    if end > 0:
                        priority = args[1:end].lower()
                        args = args[end+1:].strip()
                
                task = manager.add(args, priority=priority)
                print(f"✅ Added: {task}")
            
            elif command == "list":
                show_all = args != "pending"
                tasks = manager.list_all(show_completed=show_all)
                title = "All Tasks" if show_all else "Pending Tasks"
                print_tasks(tasks, title)
            
            elif command == "done":
                try:
                    task_id = int(args)
                    task = manager.complete(task_id)
                    if task:
                        print(f"✅ Completed: {task}")
                    else:
                        print(f"❌ Task #{task_id} not found")
                except ValueError:
                    print("❌ Please provide a valid task ID")
            
            elif command == "delete":
                try:
                    task_id = int(args)
                    if manager.delete(task_id):
                        print(f"🗑️  Deleted task #{task_id}")
                    else:
                        print(f"❌ Task #{task_id} not found")
                except ValueError:
                    print("❌ Please provide a valid task ID")
            
            elif command == "search":
                if not args:
                    print("❌ Please provide a search query")
                    continue
                results = manager.search(args)
                print_tasks(results, f"Search results for '{args}'")
            
            elif command == "stats":
                stats = manager.stats()
                print(format_stats(stats))
            
            elif command == "clear":
                count = manager.clear_completed()
                print(f"🗑️  Cleared {count} completed task(s)")
            
            else:
                print(f"❌ Unknown command: {command}")
                print("   Type 'help' for available commands")
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    run()
