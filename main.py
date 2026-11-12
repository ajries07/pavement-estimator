from drafter import *
from dataclasses import dataclass, field
import matplotlib.pyplot as plt
from bakery import assert_equal 

hide_debug_information()
set_website_title('PavePlanner')
set_website_framed(False)
set_site_information(author='Amanda Ries',
                     description='PavePlanner estimates the price to pave a certain area based on user input.',
                     sources='Utilize Chat GPT for planning, reference: Final Project 2_LLM', 
                     planning=['CS1 Final Project 0 COPY.docx','CS1 Final Project 1_ Design.docx'],
                     links='https://ajries07.github.io/pavement-estimator/', 
                     server=None)

@dataclass
class PavingProject:
    name: str
    length: float
    width: float
    price_per_sqft: float
    estimated_cost: float


@dataclass
class State:
    estimates: list[PavingProject] = field(default_factory=list)
    project_name: str = ""
    length: str = ""
    width: str = ""
    price_per_sqft: str = ""
    current_estimate: PavingProject | None = None
    selected_index: int = 0
    
def calculate_cost(length:float, width:float, price_per_sqft:float)->float:
    '''
    This function calculates the cost of paving a given area. 
    
    Args:
        length(float): the length of the area.
        width(float): the width of the area.
        price_per_sqft (float): the estimated price it would cost to pave 1 sqft.  

    Returns:
        float: The estimated price 

    '''
    if length <= 0 or width <= 0 or price_per_sqft < 0:
        return None

    return length * width * price_per_sqft

assert_equal(calculate_cost(20, 10, 5), 1000)
assert_equal(calculate_cost(30, 15, 4), 1800)
assert_equal(calculate_cost(0, 10, 5), None)
assert_equal(calculate_cost(20, -5, 5), None)

@route
def index(state: State) -> Page:
    '''
    This calls the start page. 
    
    Args:
        state(State)   

    Returns:
        Page: The start page of my website with a 'Create Estimate' button and a 'View Estimate' button. 

    '''
    return Page(state, [
        Header("PavePlanner"),
        Text("Estimate the cost of your paving project."),
        Button("Create an Estimate", "new_estimate_page"),
        Button("View Estimates", "estimates_page")
    ])


@route
def new_estimate_page(state: State) -> Page:
    '''
    This calls the start page. 
    
    Args:
        state(State)   

    Returns:
        Page: The new estimate page of my website gets user input for the length, width, and price per sqft,
        than has a 'Calculate Estimate' button to view the estimated price, and a 'Home' button to return to the home page. 

    '''
    return Page(state, [
        Header("Create a New Estimate"),
        "Project name:",
        TextBox("project_name"),
        "Length in feet:",
        TextBox("length", kind="number"),
        "Width in feet:",
        TextBox("width", kind="number"),
        "Price per square foot:",
        TextBox("price_per_sqft", kind="number"),
        Button("Calculate Estimate", "calculate_estimate"),
        Button("Home", "index")
    ])

state = State()
result = index(state)
assert_equal(result is not None, True)


@route
def calculate_estimate(state: State, project_name: str,
                       length: float, width: float,
                       price_per_sqft: float) -> Page:
    '''
    
    This page calculates the cost of paving a given area. 
    
    Args:
        state(State)
        project_name(str): this is the name of the current project. 
        length(float): the length of the area.
        width(float): the width of the area.
        price_per_sqft (float): the estimated price it would cost to pave 1 sqft.  

    Returns:
        Page: The calculate estimate page of my website gets user input for the project name, length, width, and price per sqft,
        and shows the user the estimated cost. 

    '''
    state.project_name = project_name
    state.length = str(length)
    state.width = str(width)
    state.price_per_sqft = str(price_per_sqft)

    if length <= 0 or width <= 0 or price_per_sqft < 0:
        return Page(state, [
            Header("Invalid Information"),
            "Length and width must be greater than zero. Price cannot be negative.",
            Button("Try Again", "new_estimate_page")
        ])

    area = length * width
    cost = area * price_per_sqft

    project = PavingProject(
        project_name, length, width, price_per_sqft, cost
    )

    state.estimates.append(project)
    state.current_estimate = project

    return Page(state, [
        Header("Estimate Results"),
        "Project: " + project.name,
        "Area: " + str(area) + " square feet",
        "Estimated Cost: $" + str(cost),
        Button("View All Estimates", "estimates_page"),
        Button("Home", "index")
    ])

state = State()
result = calculate_estimate(
        state, "Driveway", 20, 10, 5
    )
assert_equal(len(state.estimates), 1)
assert_equal(state.estimates[0].name, "Driveway")
assert_equal(state.estimates[0].estimated_cost, 1000)


@route
def estimates_page(state: State) -> Page:
    '''
    
    This page shows the calculated estimates.  
    
    Args:
        state(State) 

    Returns:
        Page: The estimates page of my website shows the calculated estimates from the user input. This page gives the user the option to view estimate details,
        compare estimates, delete an estimate, reset all estimates, or return home. 
    
    '''
    content = [Header("Your Estimates")]
    if len(state.estimates) == 0:
        content.append("You have not created any estimates yet.")
    else:
        for project in state.estimates:
            content.append(
                project.name + " - $" + str(project.estimated_cost)
            )

    content.extend([
        "Enter the number of the estimate you want to view (starting at 0):",
        TextBox("selected_index", 0, kind="number"),
        Button("View Estimate Details", "estimate_details_page"),
        Button("Compare Estimates", "compare_estimates_page"),
        Button("Delete an Estimate", "delete_estimate"),
        Button("Home", "index"),
        Button("Reset All Estimates", "reset_estimates")
    ])

    return Page(state, content)

state = State()
state.estimates.append(
    PavingProject("Driveway", 20, 10, 5, 1000)
)

result = estimates_page(state)
assert_equal(len(state.estimates), 1)
assert_equal(result is not None, True)


@route
def estimate_details_page(state: State, selected_index: int) -> Page:
    '''
    
    This page shows the details of a calculated estimate. 
    
    Args:
        state(State)
        selected_index(int): the project the user selects, integer based on when the entered the project (ex: first entry = 0)

    Returns:
        Page: The estimate details page of my website shows the length, width, and price the user input for a given project.
        The user can then return to the estimates page. 
    
    '''
    if selected_index < 0 or selected_index >= len(state.estimates):
        return Page(state, [
            Header("Estimate Not Found"),
            "Please enter a valid estimate number.",
            Button("Back to Estimates", "estimates_page")
        ])

    state.selected_index = selected_index
    project = state.estimates[selected_index]
    state.current_estimate = project

    return Page(state, [
        Header("Estimate Details"),
        "Project: " + project.name,
        "Length: " + str(project.length) + " feet",
        "Width: " + str(project.width) + " feet",
        "Price per square foot: $" + str(project.price_per_sqft),
        "Estimated Cost: $" + str(project.estimated_cost),
        Button("Back to Estimates", "estimates_page")
    ])

state = State()
project = PavingProject("Driveway", 20, 10, 5, 1000)
state.estimates.append(project)
result = estimate_details_page(state, 0)

assert_equal(state.selected_index, 0)
assert_equal(state.current_estimate.name, "Driveway")

@route
def compare_estimates_page(state: State) -> Page:
    '''
    
    This page compares two or more estimates that have been created. 
    
    Args:
        state(State)
        
    Returns:
        Page: The compare estimates page of my website compares the selected estimates the user wishes to compare. This page shows the user the
        estimates side by side, and gives them the option to return to the estimates page. 
    '''
    content = [Header("Compare Estimates")]

    if len(state.estimates) < 2:
        content.append("You need at least two estimates to create a comparison.")

    else:
        names = []
        costs = []

        for project in state.estimates:
            names.append(project.name)
            costs.append(project.estimated_cost)

        plt.figure(figsize=(8, 5))
        plt.bar(names, costs, color="steelblue")

        plt.title("Paving Project Cost Comparison")
        plt.xlabel("Projects")
        plt.ylabel("Estimated Cost ($)")
        plt.xticks(rotation=30)
        plt.tight_layout()

        content.append(Text("Compare the estimated costs of your projects:"))
        content.append(MatPlotLibPlot())

    content.append(Button("Back to Estimates", "estimates_page"))

    return Page(state, content)

state = State()
state.estimates.append(
    PavingProject("Driveway", 20, 10, 5, 1000)
)
state.estimates.append(
    PavingProject("Parking Lot", 30, 15, 4, 1800)
)

result = compare_estimates_page(state)

assert_equal(len(state.estimates), 2)
assert_equal(state.estimates[0].estimated_cost, 1000)
assert_equal(state.estimates[1].estimated_cost, 1800)

@route
def delete_estimate(state: State, selected_index: int) -> Page:
    '''

    This page deletes a selected estimate. 
    
    Args:
        state(State)
        selected_index(int): the project the user selects, integer based on when the entered the project (ex: first entry = 0)

    Returns:
        Page: The delete estimate page of my website deletes the estimate the user has selected. The user can then return to the estimates page with the remaining estimates. 
    
    '''
    if selected_index < 0 or selected_index >= len(state.estimates):
        return Page(state, [
            "That estimate number does not exist.",
            Button("Back to Estimates", "estimates_page")
        ])

    deleted_project = state.estimates.pop(selected_index)

    if state.current_estimate == deleted_project:
        state.current_estimate = None

    return Page(state, [
        "Deleted " + deleted_project.name,
        Button("Back to Estimates", "estimates_page")
    ])

state = State()
state.estimates.append(
    PavingProject("Driveway", 20, 10, 5, 1000)
)
result = delete_estimate(state, 0)

assert_equal(len(state.estimates), 0)

@route
def reset_estimates(state: State) -> Page:
    '''

    This page deletes all estimates. 
    
    Args:
        state(State)


    Returns:
        Page: The reset estimates page of my website deletes all estimates the user has entered. The user can then return to the home page. 
    '''
    state.estimates.clear()
    state.current_estimate = None

    return Page(state, [
        Header("Estimates Cleared"),
        "All estimates have been removed.",
        Button("Home", "index")
    ])

state = State()
state.estimates.append(
    PavingProject("Driveway", 20, 10, 5, 1000)
)
state.estimates.append(
    PavingProject("Parking Lot", 30, 15, 4, 1800)
)

result = reset_estimates(state)

assert_equal(len(state.estimates), 0)
assert_equal(state.current_estimate, None)

start_server(State())
