export class WeightedLRU<T> {
  private entries = new Map<
    string,
    { value: T; weight: number; expires: number }
  >();
  private weight = 0;
  hits = 0;
  misses = 0;
  evictions = 0;
  constructor(
    public capacity = 500000,
    public ttlMs = 300000,
  ) {}
  get(key: string): T | undefined {
    const item = this.entries.get(key);
    if (!item) {
      this.misses++;
      return;
    }
    if (item.expires <= Date.now()) {
      this.weight -= item.weight;
      this.entries.delete(key);
      this.misses++;
      return;
    }
    this.entries.delete(key);
    this.entries.set(key, item);
    this.hits++;
    return structuredClone(item.value);
  }
  set(key: string, value: T) {
    const weight = new TextEncoder().encode(JSON.stringify(value)).length;
    if (weight > this.capacity) return false;
    const old = this.entries.get(key);
    if (old) {
      this.weight -= old.weight;
      this.entries.delete(key);
    }
    while (this.weight + weight > this.capacity) {
      const key = this.entries.keys().next().value;
      if (!key) break;
      const e = this.entries.get(key)!;
      this.weight -= e.weight;
      this.entries.delete(key);
      this.evictions++;
    }
    this.entries.set(key, {
      value: structuredClone(value),
      weight,
      expires: Date.now() + this.ttlMs,
    });
    this.weight += weight;
    return true;
  }
  stats() {
    return {
      bytes: this.weight,
      capacity: this.capacity,
      entries: this.entries.size,
      hits: this.hits,
      misses: this.misses,
      evictions: this.evictions,
    };
  }
}
