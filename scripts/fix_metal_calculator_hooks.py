path = r'C:\Users\YASH SONI\Desktop\jeweller-app\frontend\src\pages\billing\MetalCalculator.tsx'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

old_block = """  const handleMetalSwitch = (m: 'Gold' | 'Silver' | 'Diamond') => {
  useEffect(() => {
    const handleCalculatorHotkeys = (e: KeyboardEvent) => {
      // Don't intercept if inside checkout modal or typing in textarea
      if (document.querySelector('.fixed.inset-0.z-50')) return;
      if ((e.altKey && (e.key === 'g' || e.key === 'G')) || e.key === 'F1') {
        e.preventDefault();
        setMetal('Gold');
        setTimeout(() => {
          const firstInput = document.querySelector<HTMLInputElement>('[data-enter-container] input:not([disabled])');
          firstInput?.focus();
          firstInput?.select();
        }, 50);
      } else if ((e.altKey && (e.key === 's' || e.key === 'S')) || e.key === 'F2') {
        e.preventDefault();
        setMetal('Silver');
        setTimeout(() => {
          const firstInput = document.querySelector<HTMLInputElement>('[data-enter-container] input:not([disabled])');
          firstInput?.focus();
          firstInput?.select();
        }, 50);
      } else if ((e.altKey && (e.key === 'd' || e.key === 'D')) || e.key === 'F3') {
        e.preventDefault();
        setMetal('Diamond');
        setTimeout(() => {
          const firstInput = document.querySelector<HTMLInputElement>('[data-enter-container] input:not([disabled])');
          firstInput?.focus();
          firstInput?.select();
        }, 50);
      }
    };
    window.addEventListener('keydown', handleCalculatorHotkeys);
    return () => window.removeEventListener('keydown', handleCalculatorHotkeys);
  }, []);
    setMetal(m);
  };"""

new_block = """  const handleMetalSwitch = (m: 'Gold' | 'Silver' | 'Diamond') => {
    setMetal(m);
  };

  useEffect(() => {
    const focusFirst = () => {
      setTimeout(() => {
        const firstInput = document.querySelector<HTMLInputElement>('[data-enter-container] input:not([disabled])');
        firstInput?.focus();
        firstInput?.select();
      }, 50);
    };

    const handleCustomSwitch = (e: any) => {
      const targetMetal = e.detail;
      if (targetMetal === 'Gold' || targetMetal === 'Silver' || targetMetal === 'Diamond') {
        setMetal(targetMetal);
        focusFirst();
      }
    };

    const handleCalculatorHotkeys = (e: KeyboardEvent) => {
      if (document.querySelector('.fixed.inset-0.z-50')) return;
      if ((e.altKey && (e.key === 'g' || e.key === 'G')) || e.key === 'F1') {
        e.preventDefault();
        setMetal('Gold');
        focusFirst();
      } else if ((e.altKey && (e.key === 's' || e.key === 'S')) || e.key === 'F2') {
        e.preventDefault();
        setMetal('Silver');
        focusFirst();
      } else if ((e.altKey && (e.key === 'd' || e.key === 'D')) || e.key === 'F3') {
        e.preventDefault();
        setMetal('Diamond');
        focusFirst();
      }
    };

    window.addEventListener('keydown', handleCalculatorHotkeys);
    window.addEventListener('switch-metal', handleCustomSwitch as EventListener);
    return () => {
      window.removeEventListener('keydown', handleCalculatorHotkeys);
      window.removeEventListener('switch-metal', handleCustomSwitch as EventListener);
    };
  }, []);"""

# Try exact or normalized replacement
text_norm = text.replace('\r\n', '\n')
old_block_norm = old_block.replace('\r\n', '\n')
new_block_norm = new_block.replace('\r\n', '\n')

assert old_block_norm in text_norm, "old_block not found in MetalCalculator.tsx"
text_norm = text_norm.replace(old_block_norm, new_block_norm, 1)

with open(path, 'w', encoding='utf-8') as f:
    f.write(text_norm)
print('Updated MetalCalculator.tsx successfully!')
