"""Part 4 exercises: reading errors, debugging, and testing with pytest."""


def sixth_item(numbers):
    """Return the sixth list item, demonstrating zero-based indexing."""
    return numbers[5]


def add(a, b, debug=False):
    """Return the sum of two values and optionally print their values."""
    if debug:
        print("a =", a, "b =", b)
    return a + b


def multiply(a, b):
    """Return the product of two values."""
    # The starter returned a + b. The failing examples showed that the
    # operation needed to be multiplication instead.
    return a * b


def run_examples():
    """Run the lesson examples without executing them during pytest imports."""
    numbers = [1, 2, 3, 4, 5, 6]
    print("Sixth item:", sixth_item(numbers))
    print("Sum:", add(1, 3, debug=True))
    print("Product:", multiply(3, 4))


if __name__ == "__main__":
    run_examples()
