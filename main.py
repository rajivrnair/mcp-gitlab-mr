from gitlab_mr import GitLabAPI, get_project_id

def main():
    """Example client code that reads project_id and creates GitLabAPI instance"""
    try:
        # Client reads project_id
        project_id = get_project_id()
        print(f"Found project_id: {project_id}")
        
        # Client creates GitLabAPI instance with project_id
        gitlab_api = GitLabAPI(project_id)
        
        # Example usage
        merge_requests = gitlab_api.get_merge_requests()
        print(f"Found {len(merge_requests)} merge requests")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
