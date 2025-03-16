# Contributing to UniV3 Single-Sided ETH Strategy

First off, thank you for considering contributing to this project! 

## How to Contribute

1. **Fork the Repository**
   - Create your own fork of the code
   - Clone the repository to your local machine

2. **Create a Branch**
   - Create a new branch for your changes
   - Use a clear branch name (e.g., `feature/add-new-rebalance-logic` or `fix/price-calculation`)

3. **Make Your Changes**
   - Follow the existing code style
   - Add comments for complex logic
   - Update documentation if needed
   - Test your changes thoroughly

4. **Write Good Commit Messages**
   - Use clear and descriptive commit messages
   - Reference issues and pull requests
   - Keep commits focused and atomic

5. **Submit a Pull Request**
   - Push your changes to your fork
   - Submit a pull request to the main repository
   - Describe your changes in detail
   - Link any relevant issues

## Development Setup

1. Install Almanak:
```bash
pip install almanak
```

2. Install dependencies:
```bash
npm install
```

3. Set up your environment variables:
```bash
cp presets/default/env .env
# Edit .env with your values
```

## Testing

1. Test your strategy locally:
```bash
almanak strat test
```

2. Ensure all states work as expected:
   - Initialization
   - Swap
   - Liquidity provision
   - Price monitoring
   - Rebalancing
   - Teardown

## Code Style Guidelines

1. **Python**
   - Follow PEP 8 guidelines
   - Use type hints
   - Document functions with docstrings

2. **Configuration**
   - Keep token addresses in constants
   - Use descriptive variable names
   - Comment complex calculations

## Questions or Problems?

Feel free to:
- Open an issue for bugs
- Start a discussion for features
- Ask questions in discussions

Thank you for your contribution! 