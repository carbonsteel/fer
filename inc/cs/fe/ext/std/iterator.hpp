#ifndef CS_FE_EXT_STD_ITERATOR_HPP
#define CS_FE_EXT_STD_ITERATOR_HPP


namespace std {

// http://stackoverflow.com/a/28139075/1275256
template <typename T>
struct reversion_wrapper { T& iterable; };

template <typename T>
auto begin (reversion_wrapper<T> w) { return rbegin(w.iterable); }

template <typename T>
auto end (reversion_wrapper<T> w) { return rend(w.iterable); }

template <typename T>
reversion_wrapper<T> reverse (T&& iterable) { return { iterable }; }

}


#endif // CS_FE_EXT_STD_ITERATOR_HPP